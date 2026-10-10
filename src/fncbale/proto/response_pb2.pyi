from fncbale.proto import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Response(_message.Message):
    __slots__ = ("ws_response", "ws_update")
    WS_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    WS_UPDATE_FIELD_NUMBER: _ClassVar[int]
    ws_response: WsResponse
    ws_update: WsUpdate
    def __init__(self, ws_response: _Optional[_Union[WsResponse, _Mapping]] = ..., ws_update: _Optional[_Union[WsUpdate, _Mapping]] = ...) -> None: ...

class WsResponse(_message.Message):
    __slots__ = ("error", "response", "index")
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    error: WsError
    response: bytes
    index: int
    def __init__(self, error: _Optional[_Union[WsError, _Mapping]] = ..., response: _Optional[bytes] = ..., index: _Optional[int] = ...) -> None: ...

class WsError(_message.Message):
    __slots__ = ("code", "message", "details")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    details: _struct_pb2.MapValue
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., details: _Optional[_Union[_struct_pb2.MapValue, _Mapping]] = ...) -> None: ...

class WsUpdate(_message.Message):
    __slots__ = ("update",)
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    update: Update
    def __init__(self, update: _Optional[_Union[Update, _Mapping]] = ...) -> None: ...

class Update(_message.Message):
    __slots__ = ("composed_update",)
    COMPOSED_UPDATE_FIELD_NUMBER: _ClassVar[int]
    composed_update: _struct_pb2.WebUpdate
    def __init__(self, composed_update: _Optional[_Union[_struct_pb2.WebUpdate, _Mapping]] = ...) -> None: ...

class StartPhoneAuth(_message.Message):
    __slots__ = ("transaction_hash", "is_registered", "sent_code_type", "code_expiration_date", "next_send_code_type", "next_send_code_wait_time", "code_timeout")
    TRANSACTION_HASH_FIELD_NUMBER: _ClassVar[int]
    IS_REGISTERED_FIELD_NUMBER: _ClassVar[int]
    SENT_CODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CODE_EXPIRATION_DATE_FIELD_NUMBER: _ClassVar[int]
    NEXT_SEND_CODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    NEXT_SEND_CODE_WAIT_TIME_FIELD_NUMBER: _ClassVar[int]
    CODE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    transaction_hash: str
    is_registered: bool
    sent_code_type: int
    code_expiration_date: _struct_pb2.Int64Value
    next_send_code_type: int
    next_send_code_wait_time: _struct_pb2.Int64Value
    code_timeout: _struct_pb2.Int32Value
    def __init__(self, transaction_hash: _Optional[str] = ..., is_registered: _Optional[bool] = ..., sent_code_type: _Optional[int] = ..., code_expiration_date: _Optional[_Union[_struct_pb2.Int64Value, _Mapping]] = ..., next_send_code_type: _Optional[int] = ..., next_send_code_wait_time: _Optional[_Union[_struct_pb2.Int64Value, _Mapping]] = ..., code_timeout: _Optional[_Union[_struct_pb2.Int32Value, _Mapping]] = ...) -> None: ...

class Auth(_message.Message):
    __slots__ = ("user", "jwt")
    USER_FIELD_NUMBER: _ClassVar[int]
    JWT_FIELD_NUMBER: _ClassVar[int]
    user: _struct_pb2.User
    jwt: _struct_pb2.StringValue
    def __init__(self, user: _Optional[_Union[_struct_pb2.User, _Mapping]] = ..., jwt: _Optional[_Union[_struct_pb2.StringValue, _Mapping]] = ...) -> None: ...

class WebCreateGroupResponse(_message.Message):
    __slots__ = ("seq", "state", "group", "users", "userPeers", "notAddedUserPeers", "inviteLink")
    SEQ_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    USERS_FIELD_NUMBER: _ClassVar[int]
    USERPEERS_FIELD_NUMBER: _ClassVar[int]
    NOTADDEDUSERPEERS_FIELD_NUMBER: _ClassVar[int]
    INVITELINK_FIELD_NUMBER: _ClassVar[int]
    seq: int
    state: bytes
    group: _struct_pb2.WebGroup
    users: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUser]
    userPeers: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUserPeer]
    notAddedUserPeers: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUserPeer]
    inviteLink: str
    def __init__(self, seq: _Optional[int] = ..., state: _Optional[bytes] = ..., group: _Optional[_Union[_struct_pb2.WebGroup, _Mapping]] = ..., users: _Optional[_Iterable[_Union[_struct_pb2.WebUser, _Mapping]]] = ..., userPeers: _Optional[_Iterable[_Union[_struct_pb2.WebUserPeer, _Mapping]]] = ..., notAddedUserPeers: _Optional[_Iterable[_Union[_struct_pb2.WebUserPeer, _Mapping]]] = ..., inviteLink: _Optional[str] = ...) -> None: ...

class WebGetContactsResponse(_message.Message):
    __slots__ = ("users", "isNotChanged", "userPeers")
    USERS_FIELD_NUMBER: _ClassVar[int]
    ISNOTCHANGED_FIELD_NUMBER: _ClassVar[int]
    USERPEERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUser]
    isNotChanged: bool
    userPeers: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUserPeer]
    def __init__(self, users: _Optional[_Iterable[_Union[_struct_pb2.WebUser, _Mapping]]] = ..., isNotChanged: _Optional[bool] = ..., userPeers: _Optional[_Iterable[_Union[_struct_pb2.WebUserPeer, _Mapping]]] = ...) -> None: ...

class WebGetDiffResponse(_message.Message):
    __slots__ = ("updates", "usersRefs", "groupsRefs")
    UPDATES_FIELD_NUMBER: _ClassVar[int]
    USERSREFS_FIELD_NUMBER: _ClassVar[int]
    GROUPSREFS_FIELD_NUMBER: _ClassVar[int]
    updates: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebT_tW_88717]
    usersRefs: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUserPeer]
    groupsRefs: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebGroupPeer]
    def __init__(self, updates: _Optional[_Iterable[_Union[_struct_pb2.WebT_tW_88717, _Mapping]]] = ..., usersRefs: _Optional[_Iterable[_Union[_struct_pb2.WebUserPeer, _Mapping]]] = ..., groupsRefs: _Optional[_Iterable[_Union[_struct_pb2.WebGroupPeer, _Mapping]]] = ...) -> None: ...

class WebGetFullGroupResponse(_message.Message):
    __slots__ = ("fullGroup",)
    FULLGROUP_FIELD_NUMBER: _ClassVar[int]
    fullGroup: _struct_pb2.WebFullGroup
    def __init__(self, fullGroup: _Optional[_Union[_struct_pb2.WebFullGroup, _Mapping]] = ...) -> None: ...

class WebGetFullUserResponse(_message.Message):
    __slots__ = ("fullUser",)
    FULLUSER_FIELD_NUMBER: _ClassVar[int]
    fullUser: _struct_pb2.WebT_n4
    def __init__(self, fullUser: _Optional[_Union[_struct_pb2.WebT_n4, _Mapping]] = ...) -> None: ...

class WebGetGroupMembersCountResponse(_message.Message):
    __slots__ = ("membersCount",)
    MEMBERSCOUNT_FIELD_NUMBER: _ClassVar[int]
    membersCount: int
    def __init__(self, membersCount: _Optional[int] = ...) -> None: ...

class WebGetMessagesViewsResponse(_message.Message):
    __slots__ = ("containers",)
    CONTAINERS_FIELD_NUMBER: _ClassVar[int]
    containers: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebT_THn]
    def __init__(self, containers: _Optional[_Iterable[_Union[_struct_pb2.WebT_THn, _Mapping]]] = ...) -> None: ...

class WebGetMyGroupsResponse(_message.Message):
    __slots__ = ("groups",)
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    groups: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebGroupPeer]
    def __init__(self, groups: _Optional[_Iterable[_Union[_struct_pb2.WebGroupPeer, _Mapping]]] = ...) -> None: ...

class WebGetNasimFileUploadUrlResponse(_message.Message):
    __slots__ = ("fileId", "url", "duplicate", "chunkSize", "blockSize")
    FILEID_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    DUPLICATE_FIELD_NUMBER: _ClassVar[int]
    CHUNKSIZE_FIELD_NUMBER: _ClassVar[int]
    BLOCKSIZE_FIELD_NUMBER: _ClassVar[int]
    fileId: int
    url: str
    duplicate: bool
    chunkSize: int
    blockSize: int
    def __init__(self, fileId: _Optional[int] = ..., url: _Optional[str] = ..., duplicate: _Optional[bool] = ..., chunkSize: _Optional[int] = ..., blockSize: _Optional[int] = ...) -> None: ...

class WebGetNasimFileUrlResponse(_message.Message):
    __slots__ = ("fileUrl",)
    FILEURL_FIELD_NUMBER: _ClassVar[int]
    fileUrl: _struct_pb2.WebFileUrl
    def __init__(self, fileUrl: _Optional[_Union[_struct_pb2.WebFileUrl, _Mapping]] = ...) -> None: ...

class WebGetNasimFileUrlsResponse(_message.Message):
    __slots__ = ("fileUrls",)
    FILEURLS_FIELD_NUMBER: _ClassVar[int]
    fileUrls: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebFileUrl]
    def __init__(self, fileUrls: _Optional[_Iterable[_Union[_struct_pb2.WebFileUrl, _Mapping]]] = ...) -> None: ...

class WebGetRoutesStatesResponse(_message.Message):
    __slots__ = ("seqs",)
    SEQS_FIELD_NUMBER: _ClassVar[int]
    seqs: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebState]
    def __init__(self, seqs: _Optional[_Iterable[_Union[_struct_pb2.WebState, _Mapping]]] = ...) -> None: ...

class WebJoinGroupResponse(_message.Message):
    __slots__ = ("group", "seq", "state", "date", "users", "rid", "userPeers", "inviterUserId", "groupSeq")
    GROUP_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    USERS_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    USERPEERS_FIELD_NUMBER: _ClassVar[int]
    INVITERUSERID_FIELD_NUMBER: _ClassVar[int]
    GROUPSEQ_FIELD_NUMBER: _ClassVar[int]
    group: _struct_pb2.WebGroup
    seq: int
    state: bytes
    date: int
    users: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUser]
    rid: int
    userPeers: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUserPeer]
    inviterUserId: int
    groupSeq: int
    def __init__(self, group: _Optional[_Union[_struct_pb2.WebGroup, _Mapping]] = ..., seq: _Optional[int] = ..., state: _Optional[bytes] = ..., date: _Optional[int] = ..., users: _Optional[_Iterable[_Union[_struct_pb2.WebUser, _Mapping]]] = ..., rid: _Optional[int] = ..., userPeers: _Optional[_Iterable[_Union[_struct_pb2.WebUserPeer, _Mapping]]] = ..., inviterUserId: _Optional[int] = ..., groupSeq: _Optional[int] = ...) -> None: ...

class WebJoinPublicGroupResponse(_message.Message):
    __slots__ = ("group", "seq", "state", "date", "users", "rid", "userPeers", "inviterUserId", "groupSeq")
    GROUP_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    USERS_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    USERPEERS_FIELD_NUMBER: _ClassVar[int]
    INVITERUSERID_FIELD_NUMBER: _ClassVar[int]
    GROUPSEQ_FIELD_NUMBER: _ClassVar[int]
    group: _struct_pb2.WebGroup
    seq: int
    state: bytes
    date: int
    users: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUser]
    rid: int
    userPeers: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUserPeer]
    inviterUserId: int
    groupSeq: int
    def __init__(self, group: _Optional[_Union[_struct_pb2.WebGroup, _Mapping]] = ..., seq: _Optional[int] = ..., state: _Optional[bytes] = ..., date: _Optional[int] = ..., users: _Optional[_Iterable[_Union[_struct_pb2.WebUser, _Mapping]]] = ..., rid: _Optional[int] = ..., userPeers: _Optional[_Iterable[_Union[_struct_pb2.WebUserPeer, _Mapping]]] = ..., inviterUserId: _Optional[int] = ..., groupSeq: _Optional[int] = ...) -> None: ...

class WebLoadDialogsResponse(_message.Message):
    __slots__ = ("groups", "users", "dialogs", "userPeers", "groupPeers")
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    USERS_FIELD_NUMBER: _ClassVar[int]
    DIALOGS_FIELD_NUMBER: _ClassVar[int]
    USERPEERS_FIELD_NUMBER: _ClassVar[int]
    GROUPPEERS_FIELD_NUMBER: _ClassVar[int]
    groups: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebGroup]
    users: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUser]
    dialogs: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebDialog]
    userPeers: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUserPeer]
    groupPeers: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebGroupPeer]
    def __init__(self, groups: _Optional[_Iterable[_Union[_struct_pb2.WebGroup, _Mapping]]] = ..., users: _Optional[_Iterable[_Union[_struct_pb2.WebUser, _Mapping]]] = ..., dialogs: _Optional[_Iterable[_Union[_struct_pb2.WebDialog, _Mapping]]] = ..., userPeers: _Optional[_Iterable[_Union[_struct_pb2.WebUserPeer, _Mapping]]] = ..., groupPeers: _Optional[_Iterable[_Union[_struct_pb2.WebGroupPeer, _Mapping]]] = ...) -> None: ...

class WebLoadGroupsResponse(_message.Message):
    __slots__ = ("groups",)
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    groups: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebGroup]
    def __init__(self, groups: _Optional[_Iterable[_Union[_struct_pb2.WebGroup, _Mapping]]] = ...) -> None: ...

class WebLoadHistoryResponse(_message.Message):
    __slots__ = ("history", "users", "userPeers", "groups", "groupPeers")
    HISTORY_FIELD_NUMBER: _ClassVar[int]
    USERS_FIELD_NUMBER: _ClassVar[int]
    USERPEERS_FIELD_NUMBER: _ClassVar[int]
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    GROUPPEERS_FIELD_NUMBER: _ClassVar[int]
    history: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebHistory]
    users: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUser]
    userPeers: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUserPeer]
    groups: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebGroup]
    groupPeers: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebGroupPeer]
    def __init__(self, history: _Optional[_Iterable[_Union[_struct_pb2.WebHistory, _Mapping]]] = ..., users: _Optional[_Iterable[_Union[_struct_pb2.WebUser, _Mapping]]] = ..., userPeers: _Optional[_Iterable[_Union[_struct_pb2.WebUserPeer, _Mapping]]] = ..., groups: _Optional[_Iterable[_Union[_struct_pb2.WebGroup, _Mapping]]] = ..., groupPeers: _Optional[_Iterable[_Union[_struct_pb2.WebGroupPeer, _Mapping]]] = ...) -> None: ...

class WebLoadMembersResponse(_message.Message):
    __slots__ = ("members", "next")
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    NEXT_FIELD_NUMBER: _ClassVar[int]
    members: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebMember]
    next: _struct_pb2.WebBytesValue
    def __init__(self, members: _Optional[_Iterable[_Union[_struct_pb2.WebMember, _Mapping]]] = ..., next: _Optional[_Union[_struct_pb2.WebBytesValue, _Mapping]] = ...) -> None: ...

class WebLoadUsersResponse(_message.Message):
    __slots__ = ("users",)
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUser]
    def __init__(self, users: _Optional[_Iterable[_Union[_struct_pb2.WebUser, _Mapping]]] = ...) -> None: ...

class WebSearchContactsResponse(_message.Message):
    __slots__ = ("users", "userPeers", "groups", "groupPeers")
    USERS_FIELD_NUMBER: _ClassVar[int]
    USERPEERS_FIELD_NUMBER: _ClassVar[int]
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    GROUPPEERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUser]
    userPeers: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUserPeer]
    groups: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebGroup]
    groupPeers: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebGroupPeer]
    def __init__(self, users: _Optional[_Iterable[_Union[_struct_pb2.WebUser, _Mapping]]] = ..., userPeers: _Optional[_Iterable[_Union[_struct_pb2.WebUserPeer, _Mapping]]] = ..., groups: _Optional[_Iterable[_Union[_struct_pb2.WebGroup, _Mapping]]] = ..., groupPeers: _Optional[_Iterable[_Union[_struct_pb2.WebGroupPeer, _Mapping]]] = ...) -> None: ...

class WebSearchPeerResponse(_message.Message):
    __slots__ = ("searchResults", "users", "groups", "userPeers", "groupPeers")
    SEARCHRESULTS_FIELD_NUMBER: _ClassVar[int]
    USERS_FIELD_NUMBER: _ClassVar[int]
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    USERPEERS_FIELD_NUMBER: _ClassVar[int]
    GROUPPEERS_FIELD_NUMBER: _ClassVar[int]
    searchResults: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebT_I_]
    users: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUser]
    groups: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebGroup]
    userPeers: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUserPeer]
    groupPeers: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebGroupPeer]
    def __init__(self, searchResults: _Optional[_Iterable[_Union[_struct_pb2.WebT_I_, _Mapping]]] = ..., users: _Optional[_Iterable[_Union[_struct_pb2.WebUser, _Mapping]]] = ..., groups: _Optional[_Iterable[_Union[_struct_pb2.WebGroup, _Mapping]]] = ..., userPeers: _Optional[_Iterable[_Union[_struct_pb2.WebUserPeer, _Mapping]]] = ..., groupPeers: _Optional[_Iterable[_Union[_struct_pb2.WebGroupPeer, _Mapping]]] = ...) -> None: ...

class WebStartPhoneAuthResponse(_message.Message):
    __slots__ = ("transactionHash", "isRegistered", "activationType", "isImeiOk", "sentCodeType", "codeExpirationDate", "nextSendCodeType", "nextSendCodeWaitTime", "codeTimeout", "exInfoAddress", "availableSendCodeTypes")
    TRANSACTIONHASH_FIELD_NUMBER: _ClassVar[int]
    ISREGISTERED_FIELD_NUMBER: _ClassVar[int]
    ACTIVATIONTYPE_FIELD_NUMBER: _ClassVar[int]
    ISIMEIOK_FIELD_NUMBER: _ClassVar[int]
    SENTCODETYPE_FIELD_NUMBER: _ClassVar[int]
    CODEEXPIRATIONDATE_FIELD_NUMBER: _ClassVar[int]
    NEXTSENDCODETYPE_FIELD_NUMBER: _ClassVar[int]
    NEXTSENDCODEWAITTIME_FIELD_NUMBER: _ClassVar[int]
    CODETIMEOUT_FIELD_NUMBER: _ClassVar[int]
    EXINFOADDRESS_FIELD_NUMBER: _ClassVar[int]
    AVAILABLESENDCODETYPES_FIELD_NUMBER: _ClassVar[int]
    transactionHash: str
    isRegistered: bool
    activationType: int
    isImeiOk: bool
    sentCodeType: int
    codeExpirationDate: _struct_pb2.WebInt64Value_1
    nextSendCodeType: int
    nextSendCodeWaitTime: _struct_pb2.WebInt64Value_1
    codeTimeout: _struct_pb2.WebInt32Value_1
    exInfoAddress: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebExInfoAddress]
    availableSendCodeTypes: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, transactionHash: _Optional[str] = ..., isRegistered: _Optional[bool] = ..., activationType: _Optional[int] = ..., isImeiOk: _Optional[bool] = ..., sentCodeType: _Optional[int] = ..., codeExpirationDate: _Optional[_Union[_struct_pb2.WebInt64Value_1, _Mapping]] = ..., nextSendCodeType: _Optional[int] = ..., nextSendCodeWaitTime: _Optional[_Union[_struct_pb2.WebInt64Value_1, _Mapping]] = ..., codeTimeout: _Optional[_Union[_struct_pb2.WebInt32Value_1, _Mapping]] = ..., exInfoAddress: _Optional[_Iterable[_Union[_struct_pb2.WebExInfoAddress, _Mapping]]] = ..., availableSendCodeTypes: _Optional[_Iterable[int]] = ...) -> None: ...

class WebT_B_(_message.Message):
    __slots__ = ("seq", "state")
    SEQ_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    seq: int
    state: bytes
    def __init__(self, seq: _Optional[int] = ..., state: _Optional[bytes] = ...) -> None: ...

class WebT_ed_47679(_message.Message):
    __slots__ = ("url",)
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str
    def __init__(self, url: _Optional[str] = ...) -> None: ...

class WebT_iF_88717(_message.Message):
    __slots__ = ("searchResults", "users", "groups", "loadMoreState", "userOutPeers", "groupOutPeers", "resultCount")
    SEARCHRESULTS_FIELD_NUMBER: _ClassVar[int]
    USERS_FIELD_NUMBER: _ClassVar[int]
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    LOADMORESTATE_FIELD_NUMBER: _ClassVar[int]
    USEROUTPEERS_FIELD_NUMBER: _ClassVar[int]
    GROUPOUTPEERS_FIELD_NUMBER: _ClassVar[int]
    RESULTCOUNT_FIELD_NUMBER: _ClassVar[int]
    searchResults: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebSearchResult]
    users: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUser]
    groups: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebGroup]
    loadMoreState: _struct_pb2.WebBytesValue
    userOutPeers: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUserPeer]
    groupOutPeers: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebGroupPeer]
    resultCount: int
    def __init__(self, searchResults: _Optional[_Iterable[_Union[_struct_pb2.WebSearchResult, _Mapping]]] = ..., users: _Optional[_Iterable[_Union[_struct_pb2.WebUser, _Mapping]]] = ..., groups: _Optional[_Iterable[_Union[_struct_pb2.WebGroup, _Mapping]]] = ..., loadMoreState: _Optional[_Union[_struct_pb2.WebBytesValue, _Mapping]] = ..., userOutPeers: _Optional[_Iterable[_Union[_struct_pb2.WebUserPeer, _Mapping]]] = ..., groupOutPeers: _Optional[_Iterable[_Union[_struct_pb2.WebGroupPeer, _Mapping]]] = ..., resultCount: _Optional[int] = ...) -> None: ...

class WebT_pQ(_message.Message):
    __slots__ = ("seq", "date", "state", "ext")
    class ExtEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    SEQ_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    seq: int
    date: int
    state: bytes
    ext: _containers.ScalarMap[str, bytes]
    def __init__(self, seq: _Optional[int] = ..., date: _Optional[int] = ..., state: _Optional[bytes] = ..., ext: _Optional[_Mapping[str, bytes]] = ...) -> None: ...

class WebT_y_68945(_message.Message):
    __slots__ = ("user", "config", "jwt")
    USER_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    JWT_FIELD_NUMBER: _ClassVar[int]
    user: _struct_pb2.WebUser
    config: _struct_pb2.WebT_TS
    jwt: _struct_pb2.WebStringValue
    def __init__(self, user: _Optional[_Union[_struct_pb2.WebUser, _Mapping]] = ..., config: _Optional[_Union[_struct_pb2.WebT_TS, _Mapping]] = ..., jwt: _Optional[_Union[_struct_pb2.WebStringValue, _Mapping]] = ...) -> None: ...
