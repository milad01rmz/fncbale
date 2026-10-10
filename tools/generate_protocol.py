"""Curate MIT protocol definitions into fncbale's isolated protobuf namespace.

Requires the pinned research snapshot only during regeneration, never at runtime.
"""

from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/step2/sources/pypi__balenova"
TARGET = ROOT / "src/fncbale/proto"
SERVICES = {
    "WebAuth",
    "WebGhasedakService",
    "WebMessaging",
    "WebGroups",
    "WebUsers",
    "WebSearch",
    "WebFiles",
    "WebAbacus",
}
METHODS = {
    "StartPhoneAuth",
    "ValidateCode",
    "ValidatePassword",
    "GetRoutesStates",
    "GetDiff",
    "SendMessage",
    "SendMultiMediaMessage",
    "UpdateMessage",
    "DeleteMessage",
    "ForwardMessages",
    "LoadHistory",
    "GetMessagesViews",
    "GetFullGroup",
    "LoadGroups",
    "GetMyGroups",
    "LoadMembers",
    "GetGroupMembersCount",
    "CreateGroup",
    "JoinGroup",
    "JoinPublicGroup",
    "GetGroupInviteURL",
    "LeaveGroup",
    "EditGroupTitle",
    "EditGroupAbout",
    "EditChannelNick",
    "InviteUser",
    "KickUser",
    "SearchPeer",
    "SearchContacts",
    "SearchMessages",
    "SearchMessageMore",
    "LoadUsers",
    "GetFullUser",
    "GetContacts",
    "EditName",
    "EditAbout",
    "EditNickName",
    "LoadDialogs",
    "GetNasimFileUploadUrl",
    "GetNasimFileUrl",
    "GetNasimFileUrls",
}


def definitions(text):
    result = {}
    for match in re.finditer(r"^(message|enum|service) (\w+)\s*\{", text, re.M):
        depth, end = 1, match.end()
        while depth:
            depth += (text[end] == "{") - (text[end] == "}")
            end += 1
        result[match[2]] = (match[1], text[match.start() : end])
    return result


def main():
    modules = {
        name: definitions((SOURCE / f"bale/proto/{name}.proto").read_text())
        for name in ("struct", "request", "response")
    }
    chosen = set()
    roots = [
        ("response", "Response"),
        ("request", "Request"),
        ("request", "KeepAliveRequest"),
        ("response", "Auth"),
        ("request", "StartPhoneAuth"),
        ("request", "ValidateCode"),
        ("request", "ValidatePassword"),
        ("response", "StartPhoneAuth"),
    ]
    rpc = []
    for name, (kind, text) in modules["response"].items():
        if kind != "service" or name not in SERVICES:
            continue
        for method, request, response in re.findall(r"rpc (\w+)\(([^)]+)\) returns \(([^)]+)\)", text):
            if method not in METHODS:
                continue
            req_module, req_name = request.split(".") if "." in request else ("response", request)
            res_module, res_name = response.split(".") if "." in response else ("response", response)
            roots.extend([(req_module, req_name), (res_module, res_name)])
            rpc.append(
                dict(
                    service=name,
                    method=method,
                    request=req_name,
                    response=res_name,
                    request_module=req_module,
                    response_module=res_module,
                )
            )
    # Use the complete current-web update shape, not the older compact dispatcher schema.
    # Independent current-web Groups SetRestriction fact (9216 codec ei):
    # groupOutPeer1, enum/int restriction2, optional wrapped nickname3; no RID.
    modules["request"]["WebSetRestrictionRequest"] = (
        "message",
        "message WebSetRestrictionRequest { struct.WebGroupPeer groupOutPeer = 1; "
        "int32 restriction = 2; struct.WebStringValue nick = 3; }",
    )
    roots.extend([("request", "WebSetRestrictionRequest"), ("response", "WebT_B_")])
    rpc.append(
        dict(
            service="WebGroups",
            method="SetRestriction",
            request="WebSetRestrictionRequest",
            response="WebT_B_",
            request_module="request",
            response_module="response",
        )
    )
    modules["response"]["Update"] = ("message", "message Update { struct.WebUpdate composed_update = 1; }")
    # The static JS extractor missed this imported/packed codec. Verified by
    # delete-packed-two.bin and independent live DeleteMessage roundtrips.
    modules["struct"]["WebT_LWL"] = ("message", "message WebT_LWL { repeated int64 dates = 1; }")
    # Current web search codec (6187, module 78637) carries a full history
    # container at field 6; the pinned extractor omitted this imported type.
    kind, text = modules["struct"]["WebT_U_34523"]
    modules["struct"]["WebT_U_34523"] = (
        kind,
        re.sub(r"\s*}$", "\n  WebHistory messageContainer = 6;\n}", text),
    )
    # Current index codec NNI/ib exposes a presence-aware author signature at 19.
    kind, text = modules["struct"]["WebHistory"]
    modules["struct"]["WebHistory"] = (kind, re.sub(r"\s*}$", "\n  WebStringValue authorSign = 19;\n}", text))
    pending = list(roots)
    while pending:
        module, name = pending.pop()
        if (module, name) in chosen:
            continue
        kind, text = modules[module][name]
        chosen.add((module, name))
        for ref in re.findall(r"\b(?:struct|request|response)\.\w+|\b[A-Z]\w*\b", text):
            other, dep = ref.split(".") if "." in ref else (module, ref)
            if dep in modules.get(other, {}) and modules[other][dep][0] != "service":
                pending.append((other, dep))
    TARGET.mkdir(parents=True, exist_ok=True)
    for module in modules:
        parts = []
        for name, (_kind, text) in modules[module].items():
            if (module, name) not in chosen:
                continue
            text = re.sub(r"\b(struct|request|response)\.", r"fncbale.wire.\1.", text)
            parts.append(text)
        imports = [
            f'import "fncbale/proto/{dep}.proto";'
            for dep in modules
            if dep != module and any(f"fncbale.wire.{dep}." in t for t in parts)
        ]
        out = "// Adapted from BaleNova 0.3.1, MIT; see THIRD_PARTY_NOTICES.md.\n"
        out += f'syntax = "proto3";\npackage fncbale.wire.{module};\n' + "\n".join(imports + parts)
        (TARGET / f"{module}.proto").write_text(out, encoding="utf-8")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "grpc_tools.protoc",
            "-I" + str(ROOT / "src"),
            "--python_out=" + str(ROOT / "src"),
            "--pyi_out=" + str(ROOT / "src"),
            *[str(TARGET / f"{m}.proto") for m in modules],
        ],
        check=True,
    )
    (TARGET / "__init__.py").write_text('"""Generated, independently namespaced wire models."""\n')
    (ROOT / "src/fncbale/capabilities.json").write_text(json.dumps(rpc, indent=2) + "\n")
    (ROOT / "licenses").mkdir(exist_ok=True)
    (ROOT / "licenses/BaleNova-MIT.txt").write_bytes(
        (SOURCE / "balenova-0.3.1.dist-info/licenses/LICENSE").read_bytes()
    )
    provenance = {
        m: hashlib.sha256((SOURCE / f"bale/proto/{m}.proto").read_bytes()).hexdigest() for m in modules
    }
    (ROOT / "docs/protocol-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    patches = {
        "facts": [
            {
                "type": "request.WebGetGroupMembersCountRequest",
                "shape": "WebGroupPeer group1; response scalar int32 membersCount1 (zero has no presence)",
                "evidence": "cached official9216 codecs ef/el and pinned MIT schema",
            },
            {
                "type": "member_count read fallback policy",
                "shape": "UNIMPLEMENTED12 alone permits full-group fallback; scalar zero needs wrapper presence",
                "evidence": "cached official8574 grpc Code enum plus independent current count/full reads",
            },
            {
                "type": "request.WebJoinPublicGroupRequest",
                "shape": "short WebBot peer1(type1,id2); no nonce; independent of private JoinGroup token1",
                "evidence": "cached official9216 codec K/Q and modulesBuilder JoinPublicGroup/JoinGroup",
            },
            {
                "type": "request.WebGetGroupInviteURLRequest",
                "shape": "WebGroupPeer groupPeer1; response.url string1",
                "evidence": "cached official9216 codecs E/L and pinned MIT schema",
            },
            {
                "type": "response.Update",
                "field": 1,
                "shape": "struct.WebUpdate composed_update",
                "evidence": "current-web envelope fixtures",
            },
            {
                "type": "struct.WebT_LWL",
                "field": 1,
                "shape": "repeated int64 dates",
                "evidence": "packed delete fixture and live roundtrips",
            },
            {
                "type": "struct.WebT_U_34523",
                "field": 6,
                "shape": "WebHistory messageContainer",
                "evidence": "cached web module 78637 codec U; golden wire test",
            },
            {
                "type": "struct.WebHistory",
                "field": 19,
                "shape": "WebStringValue authorSign",
                "evidence": "cached web NNI/ib codec; golden and live history decode",
            },
            {
                "type": "request.WebSetRestrictionRequest",
                "shape": "WebGroupPeer groupOutPeer1; int32 restriction2; WebStringValue nick3; no nonce",
                "evidence": "cached official9216 codec ei and modulesBuilder SetRestriction; PRIVATE0/PUBLIC1",
            },
        ],
        "assets": {
            name: hashlib.sha256((ROOT / "research/step2/browser/web-assets" / name).read_bytes()).hexdigest()
            for name in (
                "6187.c0643819c6.js",
                "index.4aefbadad3.js",
                "9216.fb97157470.js",
                "modulesBuilder.e7abdf3264.js",
                "8574.38a8338771.js",
            )
        },
        "generated_schema_sha256": {
            m: hashlib.sha256((TARGET / f"{m}.proto").read_bytes()).hexdigest() for m in modules
        },
        "note": "Protocol field facts supplement the pinned MIT schema; cached assets are development research, not runtime dependencies.",
    }
    (ROOT / "docs/web-protocol-patches.json").write_text(json.dumps(patches, indent=2) + "\n")
    print(f"Generated {len(chosen)} isolated definitions, {len(rpc)} curated RPC contracts")


if __name__ == "__main__":
    (ROOT / "docs").mkdir(exist_ok=True)
    main()
