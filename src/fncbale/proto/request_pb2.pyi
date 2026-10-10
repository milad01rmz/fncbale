from fncbale.proto import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Request(_message.Message):
    __slots__ = ("ws_request",)
    WS_REQUEST_FIELD_NUMBER: _ClassVar[int]
    ws_request: WsRequest
    def __init__(self, ws_request: _Optional[_Union[WsRequest, _Mapping]] = ...) -> None: ...

class WsRequest(_message.Message):
    __slots__ = ("service_name", "method", "payload", "metadata", "index")
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    service_name: str
    method: str
    payload: bytes
    metadata: Metadata
    index: int
    def __init__(self, service_name: _Optional[str] = ..., method: _Optional[str] = ..., payload: _Optional[bytes] = ..., metadata: _Optional[_Union[Metadata, _Mapping]] = ..., index: _Optional[int] = ...) -> None: ...

class MetadataComplexValues(_message.Message):
    __slots__ = ("fixed64_value",)
    FIXED64_VALUE_FIELD_NUMBER: _ClassVar[int]
    fixed64_value: int
    def __init__(self, fixed64_value: _Optional[int] = ...) -> None: ...

class MetadataValues(_message.Message):
    __slots__ = ("string_value", "msg_value")
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    MSG_VALUE_FIELD_NUMBER: _ClassVar[int]
    string_value: str
    msg_value: MetadataComplexValues
    def __init__(self, string_value: _Optional[str] = ..., msg_value: _Optional[_Union[MetadataComplexValues, _Mapping]] = ...) -> None: ...

class MetadataKeyValues(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: MetadataValues
    def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[MetadataValues, _Mapping]] = ...) -> None: ...

class Metadata(_message.Message):
    __slots__ = ("key_values",)
    KEY_VALUES_FIELD_NUMBER: _ClassVar[int]
    key_values: _containers.RepeatedCompositeFieldContainer[MetadataKeyValues]
    def __init__(self, key_values: _Optional[_Iterable[_Union[MetadataKeyValues, _Mapping]]] = ...) -> None: ...

class KeepAliveRequest(_message.Message):
    __slots__ = ("payloads",)
    PAYLOADS_FIELD_NUMBER: _ClassVar[int]
    payloads: KeepAlive
    def __init__(self, payloads: _Optional[_Union[KeepAlive, _Mapping]] = ...) -> None: ...

class KeepAlive(_message.Message):
    __slots__ = ("value_should_2",)
    VALUE_SHOULD_2_FIELD_NUMBER: _ClassVar[int]
    value_should_2: int
    def __init__(self, value_should_2: _Optional[int] = ...) -> None: ...

class StartPhoneAuth(_message.Message):
    __slots__ = ("phone_number", "app_id", "api_key", "device_hash", "device_title", "send_code_type", "options")
    PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    APP_ID_FIELD_NUMBER: _ClassVar[int]
    API_KEY_FIELD_NUMBER: _ClassVar[int]
    DEVICE_HASH_FIELD_NUMBER: _ClassVar[int]
    DEVICE_TITLE_FIELD_NUMBER: _ClassVar[int]
    SEND_CODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    phone_number: int
    app_id: int
    api_key: str
    device_hash: str
    device_title: str
    send_code_type: int
    options: bytes
    def __init__(self, phone_number: _Optional[int] = ..., app_id: _Optional[int] = ..., api_key: _Optional[str] = ..., device_hash: _Optional[str] = ..., device_title: _Optional[str] = ..., send_code_type: _Optional[int] = ..., options: _Optional[bytes] = ...) -> None: ...

class ValidateCode(_message.Message):
    __slots__ = ("transaction_hash", "code", "is_jwt")
    TRANSACTION_HASH_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    IS_JWT_FIELD_NUMBER: _ClassVar[int]
    transaction_hash: str
    code: str
    is_jwt: _struct_pb2.BoolValue
    def __init__(self, transaction_hash: _Optional[str] = ..., code: _Optional[str] = ..., is_jwt: _Optional[_Union[_struct_pb2.BoolValue, _Mapping]] = ...) -> None: ...

class ValidatePassword(_message.Message):
    __slots__ = ("transaction_hash", "password", "is_jwt")
    TRANSACTION_HASH_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    IS_JWT_FIELD_NUMBER: _ClassVar[int]
    transaction_hash: str
    password: str
    is_jwt: _struct_pb2.BoolValue
    def __init__(self, transaction_hash: _Optional[str] = ..., password: _Optional[str] = ..., is_jwt: _Optional[_Union[_struct_pb2.BoolValue, _Mapping]] = ...) -> None: ...

class WebCreateGroupRequest(_message.Message):
    __slots__ = ("rid", "title", "users", "groupType", "optimizations", "nick", "restriction")
    RID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    USERS_FIELD_NUMBER: _ClassVar[int]
    GROUPTYPE_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATIONS_FIELD_NUMBER: _ClassVar[int]
    NICK_FIELD_NUMBER: _ClassVar[int]
    RESTRICTION_FIELD_NUMBER: _ClassVar[int]
    rid: int
    title: str
    users: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUserPeer]
    groupType: int
    optimizations: _containers.RepeatedScalarFieldContainer[int]
    nick: _struct_pb2.WebStringValue
    restriction: int
    def __init__(self, rid: _Optional[int] = ..., title: _Optional[str] = ..., users: _Optional[_Iterable[_Union[_struct_pb2.WebUserPeer, _Mapping]]] = ..., groupType: _Optional[int] = ..., optimizations: _Optional[_Iterable[int]] = ..., nick: _Optional[_Union[_struct_pb2.WebStringValue, _Mapping]] = ..., restriction: _Optional[int] = ...) -> None: ...

class WebEditAboutRequest(_message.Message):
    __slots__ = ("about",)
    ABOUT_FIELD_NUMBER: _ClassVar[int]
    about: _struct_pb2.WebStringValue
    def __init__(self, about: _Optional[_Union[_struct_pb2.WebStringValue, _Mapping]] = ...) -> None: ...

class WebEditChannelNickRequest(_message.Message):
    __slots__ = ("groupPeer", "nick", "randomId")
    GROUPPEER_FIELD_NUMBER: _ClassVar[int]
    NICK_FIELD_NUMBER: _ClassVar[int]
    RANDOMID_FIELD_NUMBER: _ClassVar[int]
    groupPeer: _struct_pb2.WebGroupPeer
    nick: str
    randomId: int
    def __init__(self, groupPeer: _Optional[_Union[_struct_pb2.WebGroupPeer, _Mapping]] = ..., nick: _Optional[str] = ..., randomId: _Optional[int] = ...) -> None: ...

class WebEditGroupAboutRequest(_message.Message):
    __slots__ = ("groupPeer", "rid", "about", "optimizations")
    GROUPPEER_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    ABOUT_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATIONS_FIELD_NUMBER: _ClassVar[int]
    groupPeer: _struct_pb2.WebGroupPeer
    rid: int
    about: _struct_pb2.WebStringValue
    optimizations: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, groupPeer: _Optional[_Union[_struct_pb2.WebGroupPeer, _Mapping]] = ..., rid: _Optional[int] = ..., about: _Optional[_Union[_struct_pb2.WebStringValue, _Mapping]] = ..., optimizations: _Optional[_Iterable[int]] = ...) -> None: ...

class WebEditGroupTitleRequest(_message.Message):
    __slots__ = ("groupPeer", "title", "rid", "optimizations")
    GROUPPEER_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATIONS_FIELD_NUMBER: _ClassVar[int]
    groupPeer: _struct_pb2.WebGroupPeer
    title: str
    rid: int
    optimizations: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, groupPeer: _Optional[_Union[_struct_pb2.WebGroupPeer, _Mapping]] = ..., title: _Optional[str] = ..., rid: _Optional[int] = ..., optimizations: _Optional[_Iterable[int]] = ...) -> None: ...

class WebEditNameRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class WebEditNickNameRequest(_message.Message):
    __slots__ = ("nickname",)
    NICKNAME_FIELD_NUMBER: _ClassVar[int]
    nickname: _struct_pb2.WebStringValue
    def __init__(self, nickname: _Optional[_Union[_struct_pb2.WebStringValue, _Mapping]] = ...) -> None: ...

class WebForwardMessagesRequest(_message.Message):
    __slots__ = ("peer", "rid", "forwardedMessages", "groupedId")
    PEER_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    FORWARDEDMESSAGES_FIELD_NUMBER: _ClassVar[int]
    GROUPEDID_FIELD_NUMBER: _ClassVar[int]
    peer: _struct_pb2.WebOutPeer
    rid: _containers.RepeatedScalarFieldContainer[int]
    forwardedMessages: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebQuotedMessageReference]
    groupedId: _struct_pb2.WebInt64Value_1
    def __init__(self, peer: _Optional[_Union[_struct_pb2.WebOutPeer, _Mapping]] = ..., rid: _Optional[_Iterable[int]] = ..., forwardedMessages: _Optional[_Iterable[_Union[_struct_pb2.WebQuotedMessageReference, _Mapping]]] = ..., groupedId: _Optional[_Union[_struct_pb2.WebInt64Value_1, _Mapping]] = ...) -> None: ...

class WebGetContactsRequest(_message.Message):
    __slots__ = ("contactsHash", "optimizations")
    CONTACTSHASH_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATIONS_FIELD_NUMBER: _ClassVar[int]
    contactsHash: str
    optimizations: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, contactsHash: _Optional[str] = ..., optimizations: _Optional[_Iterable[int]] = ...) -> None: ...

class WebGetDiffRequest(_message.Message):
    __slots__ = ("states", "optimizations")
    STATES_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATIONS_FIELD_NUMBER: _ClassVar[int]
    states: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebState]
    optimizations: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, states: _Optional[_Iterable[_Union[_struct_pb2.WebState, _Mapping]]] = ..., optimizations: _Optional[_Iterable[int]] = ...) -> None: ...

class WebGetFullGroupRequest(_message.Message):
    __slots__ = ("peer",)
    PEER_FIELD_NUMBER: _ClassVar[int]
    peer: _struct_pb2.WebGroupPeer
    def __init__(self, peer: _Optional[_Union[_struct_pb2.WebGroupPeer, _Mapping]] = ...) -> None: ...

class WebGetFullUserRequest(_message.Message):
    __slots__ = ("peer",)
    PEER_FIELD_NUMBER: _ClassVar[int]
    peer: _struct_pb2.WebUserPeer
    def __init__(self, peer: _Optional[_Union[_struct_pb2.WebUserPeer, _Mapping]] = ...) -> None: ...

class WebGetGroupInviteURLRequest(_message.Message):
    __slots__ = ("groupPeer",)
    GROUPPEER_FIELD_NUMBER: _ClassVar[int]
    groupPeer: _struct_pb2.WebGroupPeer
    def __init__(self, groupPeer: _Optional[_Union[_struct_pb2.WebGroupPeer, _Mapping]] = ...) -> None: ...

class WebGetGroupMembersCountRequest(_message.Message):
    __slots__ = ("group",)
    GROUP_FIELD_NUMBER: _ClassVar[int]
    group: _struct_pb2.WebGroupPeer
    def __init__(self, group: _Optional[_Union[_struct_pb2.WebGroupPeer, _Mapping]] = ...) -> None: ...

class WebGetMessagesViewsRequest(_message.Message):
    __slots__ = ("peer", "mids", "increment", "correctMids")
    PEER_FIELD_NUMBER: _ClassVar[int]
    MIDS_FIELD_NUMBER: _ClassVar[int]
    INCREMENT_FIELD_NUMBER: _ClassVar[int]
    CORRECTMIDS_FIELD_NUMBER: _ClassVar[int]
    peer: _struct_pb2.WebPeer
    mids: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebMessageId]
    increment: bool
    correctMids: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebMessageId]
    def __init__(self, peer: _Optional[_Union[_struct_pb2.WebPeer, _Mapping]] = ..., mids: _Optional[_Iterable[_Union[_struct_pb2.WebMessageId, _Mapping]]] = ..., increment: _Optional[bool] = ..., correctMids: _Optional[_Iterable[_Union[_struct_pb2.WebMessageId, _Mapping]]] = ...) -> None: ...

class WebGetMyGroupsRequest(_message.Message):
    __slots__ = ("mode", "isOwner", "filters")
    MODE_FIELD_NUMBER: _ClassVar[int]
    ISOWNER_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    mode: int
    isOwner: bool
    filters: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebFilter]
    def __init__(self, mode: _Optional[int] = ..., isOwner: _Optional[bool] = ..., filters: _Optional[_Iterable[_Union[_struct_pb2.WebFilter, _Mapping]]] = ...) -> None: ...

class WebGetNasimFileUploadUrlRequest(_message.Message):
    __slots__ = ("expectedSize", "crc", "uid", "name", "mimeType", "exPeer", "sendType", "chunkSize")
    EXPECTEDSIZE_FIELD_NUMBER: _ClassVar[int]
    CRC_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MIMETYPE_FIELD_NUMBER: _ClassVar[int]
    EXPEER_FIELD_NUMBER: _ClassVar[int]
    SENDTYPE_FIELD_NUMBER: _ClassVar[int]
    CHUNKSIZE_FIELD_NUMBER: _ClassVar[int]
    expectedSize: int
    crc: int
    uid: int
    name: str
    mimeType: str
    exPeer: _struct_pb2.WebExPeer
    sendType: _struct_pb2.WebSendType
    chunkSize: int
    def __init__(self, expectedSize: _Optional[int] = ..., crc: _Optional[int] = ..., uid: _Optional[int] = ..., name: _Optional[str] = ..., mimeType: _Optional[str] = ..., exPeer: _Optional[_Union[_struct_pb2.WebExPeer, _Mapping]] = ..., sendType: _Optional[_Union[_struct_pb2.WebSendType, _Mapping]] = ..., chunkSize: _Optional[int] = ...) -> None: ...

class WebGetNasimFileUrlRequest(_message.Message):
    __slots__ = ("file",)
    FILE_FIELD_NUMBER: _ClassVar[int]
    file: _struct_pb2.WebFileLocation
    def __init__(self, file: _Optional[_Union[_struct_pb2.WebFileLocation, _Mapping]] = ...) -> None: ...

class WebGetNasimFileUrlsRequest(_message.Message):
    __slots__ = ("files",)
    FILES_FIELD_NUMBER: _ClassVar[int]
    files: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebFileLocation]
    def __init__(self, files: _Optional[_Iterable[_Union[_struct_pb2.WebFileLocation, _Mapping]]] = ...) -> None: ...

class WebGetRoutesStatesRequest(_message.Message):
    __slots__ = ("groupPeers", "optimizations")
    GROUPPEERS_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATIONS_FIELD_NUMBER: _ClassVar[int]
    groupPeers: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebGroupPeer]
    optimizations: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, groupPeers: _Optional[_Iterable[_Union[_struct_pb2.WebGroupPeer, _Mapping]]] = ..., optimizations: _Optional[_Iterable[int]] = ...) -> None: ...

class WebInviteUserRequest(_message.Message):
    __slots__ = ("groupPeer", "user", "rid", "optimizations", "messageCount")
    GROUPPEER_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATIONS_FIELD_NUMBER: _ClassVar[int]
    MESSAGECOUNT_FIELD_NUMBER: _ClassVar[int]
    groupPeer: _struct_pb2.WebGroupPeer
    user: _struct_pb2.WebUserPeer
    rid: int
    optimizations: _containers.RepeatedScalarFieldContainer[int]
    messageCount: _struct_pb2.WebInt32Value
    def __init__(self, groupPeer: _Optional[_Union[_struct_pb2.WebGroupPeer, _Mapping]] = ..., user: _Optional[_Union[_struct_pb2.WebUserPeer, _Mapping]] = ..., rid: _Optional[int] = ..., optimizations: _Optional[_Iterable[int]] = ..., messageCount: _Optional[_Union[_struct_pb2.WebInt32Value, _Mapping]] = ...) -> None: ...

class WebJoinGroupRequest(_message.Message):
    __slots__ = ("token", "optimizations")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATIONS_FIELD_NUMBER: _ClassVar[int]
    token: str
    optimizations: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, token: _Optional[str] = ..., optimizations: _Optional[_Iterable[int]] = ...) -> None: ...

class WebJoinPublicGroupRequest(_message.Message):
    __slots__ = ("peer", "optimizations")
    PEER_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATIONS_FIELD_NUMBER: _ClassVar[int]
    peer: _struct_pb2.WebBot
    optimizations: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, peer: _Optional[_Union[_struct_pb2.WebBot, _Mapping]] = ..., optimizations: _Optional[_Iterable[int]] = ...) -> None: ...

class WebKickUserRequest(_message.Message):
    __slots__ = ("groupPeer", "user", "rid", "optimizations")
    GROUPPEER_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATIONS_FIELD_NUMBER: _ClassVar[int]
    groupPeer: _struct_pb2.WebGroupPeer
    user: _struct_pb2.WebUserPeer
    rid: int
    optimizations: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, groupPeer: _Optional[_Union[_struct_pb2.WebGroupPeer, _Mapping]] = ..., user: _Optional[_Union[_struct_pb2.WebUserPeer, _Mapping]] = ..., rid: _Optional[int] = ..., optimizations: _Optional[_Iterable[int]] = ...) -> None: ...

class WebLeaveGroupRequest(_message.Message):
    __slots__ = ("groupPeer", "rid", "optimizations", "makeOrphan")
    GROUPPEER_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATIONS_FIELD_NUMBER: _ClassVar[int]
    MAKEORPHAN_FIELD_NUMBER: _ClassVar[int]
    groupPeer: _struct_pb2.WebGroupPeer
    rid: int
    optimizations: _containers.RepeatedScalarFieldContainer[int]
    makeOrphan: _struct_pb2.WebBoolValue_1
    def __init__(self, groupPeer: _Optional[_Union[_struct_pb2.WebGroupPeer, _Mapping]] = ..., rid: _Optional[int] = ..., optimizations: _Optional[_Iterable[int]] = ..., makeOrphan: _Optional[_Union[_struct_pb2.WebBoolValue_1, _Mapping]] = ...) -> None: ...

class WebLoadDialogsRequest(_message.Message):
    __slots__ = ("minDate", "limit", "optimizations", "dialogType", "excludePinnedDialogs", "archiveFilter")
    MINDATE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATIONS_FIELD_NUMBER: _ClassVar[int]
    DIALOGTYPE_FIELD_NUMBER: _ClassVar[int]
    EXCLUDEPINNEDDIALOGS_FIELD_NUMBER: _ClassVar[int]
    ARCHIVEFILTER_FIELD_NUMBER: _ClassVar[int]
    minDate: int
    limit: int
    optimizations: _containers.RepeatedScalarFieldContainer[int]
    dialogType: int
    excludePinnedDialogs: bool
    archiveFilter: int
    def __init__(self, minDate: _Optional[int] = ..., limit: _Optional[int] = ..., optimizations: _Optional[_Iterable[int]] = ..., dialogType: _Optional[int] = ..., excludePinnedDialogs: _Optional[bool] = ..., archiveFilter: _Optional[int] = ...) -> None: ...

class WebLoadGroupsRequest(_message.Message):
    __slots__ = ("peers",)
    PEERS_FIELD_NUMBER: _ClassVar[int]
    peers: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebGroupPeer]
    def __init__(self, peers: _Optional[_Iterable[_Union[_struct_pb2.WebGroupPeer, _Mapping]]] = ...) -> None: ...

class WebLoadHistoryRequest(_message.Message):
    __slots__ = ("peer", "date", "loadMode", "limit", "optimizations")
    PEER_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    LOADMODE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATIONS_FIELD_NUMBER: _ClassVar[int]
    peer: _struct_pb2.WebPeer
    date: int
    loadMode: int
    limit: int
    optimizations: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, peer: _Optional[_Union[_struct_pb2.WebPeer, _Mapping]] = ..., date: _Optional[int] = ..., loadMode: _Optional[int] = ..., limit: _Optional[int] = ..., optimizations: _Optional[_Iterable[int]] = ...) -> None: ...

class WebLoadMembersRequest(_message.Message):
    __slots__ = ("group", "limit", "next", "condition")
    GROUP_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    NEXT_FIELD_NUMBER: _ClassVar[int]
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    group: _struct_pb2.WebGroupPeer
    limit: int
    next: _struct_pb2.WebBytesValue
    condition: _struct_pb2.WebCondition
    def __init__(self, group: _Optional[_Union[_struct_pb2.WebGroupPeer, _Mapping]] = ..., limit: _Optional[int] = ..., next: _Optional[_Union[_struct_pb2.WebBytesValue, _Mapping]] = ..., condition: _Optional[_Union[_struct_pb2.WebCondition, _Mapping]] = ...) -> None: ...

class WebLoadUsersRequest(_message.Message):
    __slots__ = ("peers",)
    PEERS_FIELD_NUMBER: _ClassVar[int]
    peers: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebUserPeer]
    def __init__(self, peers: _Optional[_Iterable[_Union[_struct_pb2.WebUserPeer, _Mapping]]] = ...) -> None: ...

class WebSearchContactsRequest(_message.Message):
    __slots__ = ("request", "optimizations")
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATIONS_FIELD_NUMBER: _ClassVar[int]
    request: str
    optimizations: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, request: _Optional[str] = ..., optimizations: _Optional[_Iterable[int]] = ...) -> None: ...

class WebSearchMessageMoreRequest(_message.Message):
    __slots__ = ("loadMoreState", "query", "optimizations")
    LOADMORESTATE_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATIONS_FIELD_NUMBER: _ClassVar[int]
    loadMoreState: _struct_pb2.WebBytesValue
    query: _struct_pb2.WebAndQuery
    optimizations: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, loadMoreState: _Optional[_Union[_struct_pb2.WebBytesValue, _Mapping]] = ..., query: _Optional[_Union[_struct_pb2.WebAndQuery, _Mapping]] = ..., optimizations: _Optional[_Iterable[int]] = ...) -> None: ...

class WebSearchMessagesRequest(_message.Message):
    __slots__ = ("query", "optimizations")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATIONS_FIELD_NUMBER: _ClassVar[int]
    query: _struct_pb2.WebAndQuery
    optimizations: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, query: _Optional[_Union[_struct_pb2.WebAndQuery, _Mapping]] = ..., optimizations: _Optional[_Iterable[int]] = ...) -> None: ...

class WebSearchPeerRequest(_message.Message):
    __slots__ = ("query", "optimizations")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATIONS_FIELD_NUMBER: _ClassVar[int]
    query: _containers.RepeatedCompositeFieldContainer[_struct_pb2.WebAndQuery]
    optimizations: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, query: _Optional[_Iterable[_Union[_struct_pb2.WebAndQuery, _Mapping]]] = ..., optimizations: _Optional[_Iterable[int]] = ...) -> None: ...

class WebSetRestrictionRequest(_message.Message):
    __slots__ = ("groupOutPeer", "restriction", "nick")
    GROUPOUTPEER_FIELD_NUMBER: _ClassVar[int]
    RESTRICTION_FIELD_NUMBER: _ClassVar[int]
    NICK_FIELD_NUMBER: _ClassVar[int]
    groupOutPeer: _struct_pb2.WebGroupPeer
    restriction: int
    nick: _struct_pb2.WebStringValue
    def __init__(self, groupOutPeer: _Optional[_Union[_struct_pb2.WebGroupPeer, _Mapping]] = ..., restriction: _Optional[int] = ..., nick: _Optional[_Union[_struct_pb2.WebStringValue, _Mapping]] = ...) -> None: ...

class WebStartPhoneAuthRequest(_message.Message):
    __slots__ = ("phoneNumber", "appId", "apiKey", "deviceHash", "deviceTitle", "timeZone", "preferredLanguages", "imeiList", "sendCodeType", "options")
    PHONENUMBER_FIELD_NUMBER: _ClassVar[int]
    APPID_FIELD_NUMBER: _ClassVar[int]
    APIKEY_FIELD_NUMBER: _ClassVar[int]
    DEVICEHASH_FIELD_NUMBER: _ClassVar[int]
    DEVICETITLE_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    PREFERREDLANGUAGES_FIELD_NUMBER: _ClassVar[int]
    IMEILIST_FIELD_NUMBER: _ClassVar[int]
    SENDCODETYPE_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    phoneNumber: int
    appId: int
    apiKey: str
    deviceHash: bytes
    deviceTitle: str
    timeZone: _struct_pb2.WebStringValue
    preferredLanguages: _containers.RepeatedScalarFieldContainer[str]
    imeiList: _struct_pb2.WebValue
    sendCodeType: int
    options: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, phoneNumber: _Optional[int] = ..., appId: _Optional[int] = ..., apiKey: _Optional[str] = ..., deviceHash: _Optional[bytes] = ..., deviceTitle: _Optional[str] = ..., timeZone: _Optional[_Union[_struct_pb2.WebStringValue, _Mapping]] = ..., preferredLanguages: _Optional[_Iterable[str]] = ..., imeiList: _Optional[_Union[_struct_pb2.WebValue, _Mapping]] = ..., sendCodeType: _Optional[int] = ..., options: _Optional[_Iterable[int]] = ...) -> None: ...

class WebUpdateMessageRequest(_message.Message):
    __slots__ = ("peer", "rid", "updatedMessage")
    PEER_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    UPDATEDMESSAGE_FIELD_NUMBER: _ClassVar[int]
    peer: _struct_pb2.WebPeer
    rid: int
    updatedMessage: _struct_pb2.WebMessage
    def __init__(self, peer: _Optional[_Union[_struct_pb2.WebPeer, _Mapping]] = ..., rid: _Optional[int] = ..., updatedMessage: _Optional[_Union[_struct_pb2.WebMessage, _Mapping]] = ...) -> None: ...

class WebValidateCodeRequest(_message.Message):
    __slots__ = ("transactionHash", "code", "isJwt", "futureAuthTokens")
    TRANSACTIONHASH_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    ISJWT_FIELD_NUMBER: _ClassVar[int]
    FUTUREAUTHTOKENS_FIELD_NUMBER: _ClassVar[int]
    transactionHash: str
    code: str
    isJwt: _struct_pb2.WebBoolValue_1
    futureAuthTokens: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, transactionHash: _Optional[str] = ..., code: _Optional[str] = ..., isJwt: _Optional[_Union[_struct_pb2.WebBoolValue_1, _Mapping]] = ..., futureAuthTokens: _Optional[_Iterable[str]] = ...) -> None: ...

class WebValidatePasswordRequest(_message.Message):
    __slots__ = ("transactionHash", "password", "isJwt")
    TRANSACTIONHASH_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    ISJWT_FIELD_NUMBER: _ClassVar[int]
    transactionHash: str
    password: str
    isJwt: _struct_pb2.WebBoolValue_1
    def __init__(self, transactionHash: _Optional[str] = ..., password: _Optional[str] = ..., isJwt: _Optional[_Union[_struct_pb2.WebBoolValue_1, _Mapping]] = ...) -> None: ...
