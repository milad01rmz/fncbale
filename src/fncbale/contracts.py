"""Curated method registry. Static presence never enables ambiguous write retry."""

from dataclasses import dataclass
from importlib.resources import files
import json

from .proto import request_pb2, response_pb2, struct_pb2

SERVICES = {
    "WebAuth": "bale.auth.v1.Auth",
    "WebMessaging": "bale.messaging.v2.Messaging",
    "WebGroups": "bale.groups.v1.Groups",
    "WebUsers": "bale.users.v1.Users",
    "WebSearch": "bale.search.v1.Search",
    "WebGhasedakService": "bale.ghasedak.v1.GhasedakService",
    "WebFiles": "ai.bale.server.Files",
    "WebAbacus": "bale.abacus.v1.Abacus",
}
READS = {
    "GetRoutesStates",
    "GetDiff",
    "LoadHistory",
    "GetFullGroup",
    "LoadGroups",
    "GetMyGroups",
    "GetGroupInviteURL",
    "LoadMembers",
    "GetGroupMembersCount",
    "SearchPeer",
    "SearchContacts",
    "SearchMessages",
    "SearchMessageMore",
    "LoadUsers",
    "GetFullUser",
    "GetContacts",
    "LoadDialogs",
    "GetNasimFileUrl",
    "GetNasimFileUrls",
}
LIVE_VERIFIED = {
    "SendMessage",
    "SendMultiMediaMessage",
    "UpdateMessage",
    "DeleteMessage",
    "ForwardMessages",
    "LoadHistory",
    "GetFullGroup",
    "LoadMembers",
    "GetMessagesViews",
    "GetRoutesStates",
    "GetDiff",
    "GetNasimFileUploadUrl",
    "GetNasimFileUrl",
    "StartPhoneAuth",
    "ValidateCode",
}
MODULES = {"request": request_pb2, "response": response_pb2, "struct": struct_pb2}


@dataclass(frozen=True, slots=True)
class Contract:
    service: str
    method: str
    request: type
    response: type
    readonly: bool
    evidence: str


REGISTRY = {}
for record in json.loads(files("fncbale").joinpath("capabilities.json").read_text()):
    service = SERVICES[record["service"]]
    REGISTRY[record["method"]] = Contract(
        service,
        record["method"],
        getattr(MODULES[record["request_module"]], record["request"]),
        getattr(MODULES[record["response_module"]], record["response"]),
        record["method"] in READS,
        "research-live" if record["method"] in LIVE_VERIFIED else "experimental",
    )


def contract(method):
    return REGISTRY[method]
