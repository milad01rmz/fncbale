from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExPeerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EX_PEER_TYPE_UNKNOWN: _ClassVar[ExPeerType]
    EX_PEER_TYPE_PRIVATE: _ClassVar[ExPeerType]
    EX_PEER_TYPE_GROUP: _ClassVar[ExPeerType]
    EX_PEER_TYPE_CHANNEL: _ClassVar[ExPeerType]
    EX_PEER_TYPE_BOT: _ClassVar[ExPeerType]
    EX_PEER_TYPE_SUPERGROUP: _ClassVar[ExPeerType]
    EX_PEER_TYPE_THREAD: _ClassVar[ExPeerType]

class Sex(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SEX_UNKNOWN: _ClassVar[Sex]
    SEX_MALE: _ClassVar[Sex]
    SEX_FEMALE: _ClassVar[Sex]
EX_PEER_TYPE_UNKNOWN: ExPeerType
EX_PEER_TYPE_PRIVATE: ExPeerType
EX_PEER_TYPE_GROUP: ExPeerType
EX_PEER_TYPE_CHANNEL: ExPeerType
EX_PEER_TYPE_BOT: ExPeerType
EX_PEER_TYPE_SUPERGROUP: ExPeerType
EX_PEER_TYPE_THREAD: ExPeerType
SEX_UNKNOWN: Sex
SEX_MALE: Sex
SEX_FEMALE: Sex

class FastThumb(_message.Message):
    __slots__ = ("w", "h", "thumb")
    W_FIELD_NUMBER: _ClassVar[int]
    H_FIELD_NUMBER: _ClassVar[int]
    THUMB_FIELD_NUMBER: _ClassVar[int]
    w: int
    h: int
    thumb: bytes
    def __init__(self, w: _Optional[int] = ..., h: _Optional[int] = ..., thumb: _Optional[bytes] = ...) -> None: ...

class IntroPhoto(_message.Message):
    __slots__ = ("thumb", "width", "height")
    THUMB_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    thumb: FastThumb
    width: int
    height: int
    def __init__(self, thumb: _Optional[_Union[FastThumb, _Mapping]] = ..., width: _Optional[int] = ..., height: _Optional[int] = ...) -> None: ...

class IntroGif(_message.Message):
    __slots__ = ("thumb", "width", "height")
    THUMB_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    thumb: FastThumb
    width: int
    height: int
    def __init__(self, thumb: _Optional[_Union[FastThumb, _Mapping]] = ..., width: _Optional[int] = ..., height: _Optional[int] = ...) -> None: ...

class MediaExt(_message.Message):
    __slots__ = ("intro_gif", "intro_photo")
    INTRO_GIF_FIELD_NUMBER: _ClassVar[int]
    INTRO_PHOTO_FIELD_NUMBER: _ClassVar[int]
    intro_gif: IntroGif
    intro_photo: IntroPhoto
    def __init__(self, intro_gif: _Optional[_Union[IntroGif, _Mapping]] = ..., intro_photo: _Optional[_Union[IntroPhoto, _Mapping]] = ...) -> None: ...

class IntroMedia(_message.Message):
    __slots__ = ("file_location", "file_size", "mime_type", "file_name", "media_extra")
    FILE_LOCATION_FIELD_NUMBER: _ClassVar[int]
    FILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    MEDIA_EXTRA_FIELD_NUMBER: _ClassVar[int]
    file_location: FileLocation
    file_size: int
    mime_type: str
    file_name: str
    media_extra: MediaExt
    def __init__(self, file_location: _Optional[_Union[FileLocation, _Mapping]] = ..., file_size: _Optional[int] = ..., mime_type: _Optional[str] = ..., file_name: _Optional[str] = ..., media_extra: _Optional[_Union[MediaExt, _Mapping]] = ...) -> None: ...

class IntroMessage(_message.Message):
    __slots__ = ("text", "media")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    MEDIA_FIELD_NUMBER: _ClassVar[int]
    text: StringValue
    media: IntroMedia
    def __init__(self, text: _Optional[_Union[StringValue, _Mapping]] = ..., media: _Optional[_Union[IntroMedia, _Mapping]] = ...) -> None: ...

class Intro(_message.Message):
    __slots__ = ("text", "file_location", "width", "height", "file_size", "mime_type", "file_name", "thumb")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    FILE_LOCATION_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    THUMB_FIELD_NUMBER: _ClassVar[int]
    text: StringValue
    file_location: FileLocation
    width: int
    height: int
    file_size: int
    mime_type: str
    file_name: str
    thumb: FastThumb
    def __init__(self, text: _Optional[_Union[StringValue, _Mapping]] = ..., file_location: _Optional[_Union[FileLocation, _Mapping]] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., file_size: _Optional[int] = ..., mime_type: _Optional[str] = ..., file_name: _Optional[str] = ..., thumb: _Optional[_Union[FastThumb, _Mapping]] = ...) -> None: ...

class BotExInfo(_message.Message):
    __slots__ = ("bot_active_users", "has_main_mini_app", "intro", "intro_message", "has_timche_profile", "has_multiple_topics", "allow_topic_creation")
    BOT_ACTIVE_USERS_FIELD_NUMBER: _ClassVar[int]
    HAS_MAIN_MINI_APP_FIELD_NUMBER: _ClassVar[int]
    INTRO_FIELD_NUMBER: _ClassVar[int]
    INTRO_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    HAS_TIMCHE_PROFILE_FIELD_NUMBER: _ClassVar[int]
    HAS_MULTIPLE_TOPICS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_TOPIC_CREATION_FIELD_NUMBER: _ClassVar[int]
    bot_active_users: StringValue
    has_main_mini_app: BoolValue
    intro: Intro
    intro_message: IntroMessage
    has_timche_profile: BoolValue
    has_multiple_topics: bool
    allow_topic_creation: bool
    def __init__(self, bot_active_users: _Optional[_Union[StringValue, _Mapping]] = ..., has_main_mini_app: _Optional[_Union[BoolValue, _Mapping]] = ..., intro: _Optional[_Union[Intro, _Mapping]] = ..., intro_message: _Optional[_Union[IntroMessage, _Mapping]] = ..., has_timche_profile: _Optional[_Union[BoolValue, _Mapping]] = ..., has_multiple_topics: _Optional[bool] = ..., allow_topic_creation: _Optional[bool] = ...) -> None: ...

class ExInfo(_message.Message):
    __slots__ = ("ex_peer_type", "identified")
    EX_PEER_TYPE_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIED_FIELD_NUMBER: _ClassVar[int]
    ex_peer_type: ExPeerType
    identified: BoolValue
    def __init__(self, ex_peer_type: _Optional[_Union[ExPeerType, str]] = ..., identified: _Optional[_Union[BoolValue, _Mapping]] = ...) -> None: ...

class Int64Value(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class BoolValue(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: bool
    def __init__(self, value: _Optional[bool] = ...) -> None: ...

class FileLocation(_message.Message):
    __slots__ = ("file_id", "access_hash", "file_storage_version")
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    ACCESS_HASH_FIELD_NUMBER: _ClassVar[int]
    FILE_STORAGE_VERSION_FIELD_NUMBER: _ClassVar[int]
    file_id: int
    access_hash: int
    file_storage_version: Int32Value
    def __init__(self, file_id: _Optional[int] = ..., access_hash: _Optional[int] = ..., file_storage_version: _Optional[_Union[Int32Value, _Mapping]] = ...) -> None: ...

class AvatarImage(_message.Message):
    __slots__ = ("file_location", "width", "height", "file_size")
    FILE_LOCATION_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    file_location: FileLocation
    width: int
    height: int
    file_size: int
    def __init__(self, file_location: _Optional[_Union[FileLocation, _Mapping]] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., file_size: _Optional[int] = ...) -> None: ...

class Avatar(_message.Message):
    __slots__ = ("small_image", "large_image", "full_image", "id", "date")
    SMALL_IMAGE_FIELD_NUMBER: _ClassVar[int]
    LARGE_IMAGE_FIELD_NUMBER: _ClassVar[int]
    FULL_IMAGE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    small_image: AvatarImage
    large_image: AvatarImage
    full_image: AvatarImage
    id: Int64Value
    date: Int64Value
    def __init__(self, small_image: _Optional[_Union[AvatarImage, _Mapping]] = ..., large_image: _Optional[_Union[AvatarImage, _Mapping]] = ..., full_image: _Optional[_Union[AvatarImage, _Mapping]] = ..., id: _Optional[_Union[Int64Value, _Mapping]] = ..., date: _Optional[_Union[Int64Value, _Mapping]] = ...) -> None: ...

class StringValue(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class ArrayValue(_message.Message):
    __slots__ = ("array",)
    ARRAY_FIELD_NUMBER: _ClassVar[int]
    array: _containers.RepeatedCompositeFieldContainer[RawValue]
    def __init__(self, array: _Optional[_Iterable[_Union[RawValue, _Mapping]]] = ...) -> None: ...

class RawValue(_message.Message):
    __slots__ = ("string_value", "boolean_value", "int32_value", "int64_value", "double_value", "array_value")
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    BOOLEAN_VALUE_FIELD_NUMBER: _ClassVar[int]
    INT32_VALUE_FIELD_NUMBER: _ClassVar[int]
    INT64_VALUE_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    ARRAY_VALUE_FIELD_NUMBER: _ClassVar[int]
    string_value: str
    boolean_value: bool
    int32_value: int
    int64_value: int
    double_value: float
    array_value: ArrayValue
    def __init__(self, string_value: _Optional[str] = ..., boolean_value: _Optional[bool] = ..., int32_value: _Optional[int] = ..., int64_value: _Optional[int] = ..., double_value: _Optional[float] = ..., array_value: _Optional[_Union[ArrayValue, _Mapping]] = ...) -> None: ...

class MapValueItem(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: RawValue
    def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[RawValue, _Mapping]] = ...) -> None: ...

class MapValue(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[MapValueItem]
    def __init__(self, items: _Optional[_Iterable[_Union[MapValueItem, _Mapping]]] = ...) -> None: ...

class User(_message.Message):
    __slots__ = ("id", "access_hash", "name", "local_name", "sex", "avatar", "is_bot", "nick", "ext", "state_version", "is_deleted", "contact_info", "puppeteer", "created_at", "ex_info", "bot_ex_info")
    class ExtEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: RawValue
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[RawValue, _Mapping]] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    ACCESS_HASH_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LOCAL_NAME_FIELD_NUMBER: _ClassVar[int]
    SEX_FIELD_NUMBER: _ClassVar[int]
    AVATAR_FIELD_NUMBER: _ClassVar[int]
    IS_BOT_FIELD_NUMBER: _ClassVar[int]
    NICK_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    STATE_VERSION_FIELD_NUMBER: _ClassVar[int]
    IS_DELETED_FIELD_NUMBER: _ClassVar[int]
    CONTACT_INFO_FIELD_NUMBER: _ClassVar[int]
    PUPPETEER_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    EX_INFO_FIELD_NUMBER: _ClassVar[int]
    BOT_EX_INFO_FIELD_NUMBER: _ClassVar[int]
    id: int
    access_hash: int
    name: str
    local_name: StringValue
    sex: Sex
    avatar: Avatar
    is_bot: BoolValue
    nick: StringValue
    ext: _containers.MessageMap[str, RawValue]
    state_version: Int64Value
    is_deleted: BoolValue
    contact_info: _containers.RepeatedCompositeFieldContainer[ContactInfo]
    puppeteer: int
    created_at: Int64Value
    ex_info: ExInfo
    bot_ex_info: BotExInfo
    def __init__(self, id: _Optional[int] = ..., access_hash: _Optional[int] = ..., name: _Optional[str] = ..., local_name: _Optional[_Union[StringValue, _Mapping]] = ..., sex: _Optional[_Union[Sex, str]] = ..., avatar: _Optional[_Union[Avatar, _Mapping]] = ..., is_bot: _Optional[_Union[BoolValue, _Mapping]] = ..., nick: _Optional[_Union[StringValue, _Mapping]] = ..., ext: _Optional[_Mapping[str, RawValue]] = ..., state_version: _Optional[_Union[Int64Value, _Mapping]] = ..., is_deleted: _Optional[_Union[BoolValue, _Mapping]] = ..., contact_info: _Optional[_Iterable[_Union[ContactInfo, _Mapping]]] = ..., puppeteer: _Optional[int] = ..., created_at: _Optional[_Union[Int64Value, _Mapping]] = ..., ex_info: _Optional[_Union[ExInfo, _Mapping]] = ..., bot_ex_info: _Optional[_Union[BotExInfo, _Mapping]] = ...) -> None: ...

class ContactInfo(_message.Message):
    __slots__ = ("type", "string_value", "long_value", "title", "subtitle", "type_spec")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    LONG_VALUE_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    SUBTITLE_FIELD_NUMBER: _ClassVar[int]
    TYPE_SPEC_FIELD_NUMBER: _ClassVar[int]
    type: int
    string_value: StringValue
    long_value: Int64Value
    title: StringValue
    subtitle: StringValue
    type_spec: StringValue
    def __init__(self, type: _Optional[int] = ..., string_value: _Optional[_Union[StringValue, _Mapping]] = ..., long_value: _Optional[_Union[Int64Value, _Mapping]] = ..., title: _Optional[_Union[StringValue, _Mapping]] = ..., subtitle: _Optional[_Union[StringValue, _Mapping]] = ..., type_spec: _Optional[_Union[StringValue, _Mapping]] = ...) -> None: ...

class Int32Value(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class WebAccountDeleted(_message.Message):
    __slots__ = ("userId",)
    USERID_FIELD_NUMBER: _ClassVar[int]
    userId: int
    def __init__(self, userId: _Optional[int] = ...) -> None: ...

class WebAction(_message.Message):
    __slots__ = ("raiseHand", "lowerHand")
    RAISEHAND_FIELD_NUMBER: _ClassVar[int]
    LOWERHAND_FIELD_NUMBER: _ClassVar[int]
    raiseHand: WebRaiseHand
    lowerHand: WebLowerHand
    def __init__(self, raiseHand: _Optional[_Union[WebRaiseHand, _Mapping]] = ..., lowerHand: _Optional[_Union[WebLowerHand, _Mapping]] = ...) -> None: ...

class WebAdvertisementMessage(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebAllContactsRemoved(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebAndQuery(_message.Message):
    __slots__ = ("searchAndCondition", "searchOrCondition", "searchPeerCondition", "searchPeerContentType", "searchPeerTypeCondition", "searchPieceText", "searchDate", "searchSender", "searchHasLink", "searchDocumentName", "searchScopeCondition")
    SEARCHANDCONDITION_FIELD_NUMBER: _ClassVar[int]
    SEARCHORCONDITION_FIELD_NUMBER: _ClassVar[int]
    SEARCHPEERCONDITION_FIELD_NUMBER: _ClassVar[int]
    SEARCHPEERCONTENTTYPE_FIELD_NUMBER: _ClassVar[int]
    SEARCHPEERTYPECONDITION_FIELD_NUMBER: _ClassVar[int]
    SEARCHPIECETEXT_FIELD_NUMBER: _ClassVar[int]
    SEARCHDATE_FIELD_NUMBER: _ClassVar[int]
    SEARCHSENDER_FIELD_NUMBER: _ClassVar[int]
    SEARCHHASLINK_FIELD_NUMBER: _ClassVar[int]
    SEARCHDOCUMENTNAME_FIELD_NUMBER: _ClassVar[int]
    SEARCHSCOPECONDITION_FIELD_NUMBER: _ClassVar[int]
    searchAndCondition: WebSearchAndCondition
    searchOrCondition: WebSearchOrCondition
    searchPeerCondition: WebSearchPeerCondition
    searchPeerContentType: WebSearchPeerContentType
    searchPeerTypeCondition: WebSearchPeerTypeCondition
    searchPieceText: WebQuery
    searchDate: WebSearchDate
    searchSender: WebSearchSender
    searchHasLink: WebSearchHasLink
    searchDocumentName: WebSearchDocumentName
    searchScopeCondition: WebSearchScopeCondition
    def __init__(self, searchAndCondition: _Optional[_Union[WebSearchAndCondition, _Mapping]] = ..., searchOrCondition: _Optional[_Union[WebSearchOrCondition, _Mapping]] = ..., searchPeerCondition: _Optional[_Union[WebSearchPeerCondition, _Mapping]] = ..., searchPeerContentType: _Optional[_Union[WebSearchPeerContentType, _Mapping]] = ..., searchPeerTypeCondition: _Optional[_Union[WebSearchPeerTypeCondition, _Mapping]] = ..., searchPieceText: _Optional[_Union[WebQuery, _Mapping]] = ..., searchDate: _Optional[_Union[WebSearchDate, _Mapping]] = ..., searchSender: _Optional[_Union[WebSearchSender, _Mapping]] = ..., searchHasLink: _Optional[_Union[WebSearchHasLink, _Mapping]] = ..., searchDocumentName: _Optional[_Union[WebSearchDocumentName, _Mapping]] = ..., searchScopeCondition: _Optional[_Union[WebSearchScopeCondition, _Mapping]] = ...) -> None: ...

class WebAnimatedSticker(_message.Message):
    __slots__ = ("id", "emoji", "fileLocation")
    ID_FIELD_NUMBER: _ClassVar[int]
    EMOJI_FIELD_NUMBER: _ClassVar[int]
    FILELOCATION_FIELD_NUMBER: _ClassVar[int]
    id: int
    emoji: WebStringValue
    fileLocation: WebImageLocation
    def __init__(self, id: _Optional[int] = ..., emoji: _Optional[_Union[WebStringValue, _Mapping]] = ..., fileLocation: _Optional[_Union[WebImageLocation, _Mapping]] = ...) -> None: ...

class WebAnimatedStickerMessage(_message.Message):
    __slots__ = ("stickerId", "fastPreview", "fileLocation", "stickerCollectionId", "stickerCollectionAccessHash")
    STICKERID_FIELD_NUMBER: _ClassVar[int]
    FASTPREVIEW_FIELD_NUMBER: _ClassVar[int]
    FILELOCATION_FIELD_NUMBER: _ClassVar[int]
    STICKERCOLLECTIONID_FIELD_NUMBER: _ClassVar[int]
    STICKERCOLLECTIONACCESSHASH_FIELD_NUMBER: _ClassVar[int]
    stickerId: WebInt32Value
    fastPreview: WebBytesValue
    fileLocation: WebImageLocation
    stickerCollectionId: WebInt32Value
    stickerCollectionAccessHash: WebInt64Value_1
    def __init__(self, stickerId: _Optional[_Union[WebInt32Value, _Mapping]] = ..., fastPreview: _Optional[_Union[WebBytesValue, _Mapping]] = ..., fileLocation: _Optional[_Union[WebImageLocation, _Mapping]] = ..., stickerCollectionId: _Optional[_Union[WebInt32Value, _Mapping]] = ..., stickerCollectionAccessHash: _Optional[_Union[WebInt64Value_1, _Mapping]] = ...) -> None: ...

class WebAskBotReview(_message.Message):
    __slots__ = ("botId", "previousRating", "previousComment", "payload")
    BOTID_FIELD_NUMBER: _ClassVar[int]
    PREVIOUSRATING_FIELD_NUMBER: _ClassVar[int]
    PREVIOUSCOMMENT_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    botId: int
    previousRating: WebInt32Value
    previousComment: WebStringValue
    payload: WebStringValue
    def __init__(self, botId: _Optional[int] = ..., previousRating: _Optional[_Union[WebInt32Value, _Mapping]] = ..., previousComment: _Optional[_Union[WebStringValue, _Mapping]] = ..., payload: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebAttache(_message.Message):
    __slots__ = ("title", "titleUrl", "titleIcon", "text", "style", "fields")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    TITLEURL_FIELD_NUMBER: _ClassVar[int]
    TITLEICON_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    STYLE_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    title: WebStringValue
    titleUrl: WebStringValue
    titleIcon: WebImageLocation
    text: WebStringValue
    style: WebStyle
    fields: _containers.RepeatedCompositeFieldContainer[WebField]
    def __init__(self, title: _Optional[_Union[WebStringValue, _Mapping]] = ..., titleUrl: _Optional[_Union[WebStringValue, _Mapping]] = ..., titleIcon: _Optional[_Union[WebImageLocation, _Mapping]] = ..., text: _Optional[_Union[WebStringValue, _Mapping]] = ..., style: _Optional[_Union[WebStyle, _Mapping]] = ..., fields: _Optional[_Iterable[_Union[WebField, _Mapping]]] = ...) -> None: ...

class WebAttributes(_message.Message):
    __slots__ = ("isMentioned", "isHighlighted", "isNotified", "isOnlyForYou")
    ISMENTIONED_FIELD_NUMBER: _ClassVar[int]
    ISHIGHLIGHTED_FIELD_NUMBER: _ClassVar[int]
    ISNOTIFIED_FIELD_NUMBER: _ClassVar[int]
    ISONLYFORYOU_FIELD_NUMBER: _ClassVar[int]
    isMentioned: WebBoolValue_1
    isHighlighted: WebBoolValue_1
    isNotified: WebBoolValue_1
    isOnlyForYou: WebBoolValue_1
    def __init__(self, isMentioned: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., isHighlighted: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., isNotified: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., isOnlyForYou: _Optional[_Union[WebBoolValue_1, _Mapping]] = ...) -> None: ...

class WebAuthentication(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebAvatar(_message.Message):
    __slots__ = ("smallImage", "largeImage", "fullImage", "id", "date")
    SMALLIMAGE_FIELD_NUMBER: _ClassVar[int]
    LARGEIMAGE_FIELD_NUMBER: _ClassVar[int]
    FULLIMAGE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    smallImage: WebSmallImage
    largeImage: WebSmallImage
    fullImage: WebSmallImage
    id: WebInt64Value_1
    date: WebInt64Value_1
    def __init__(self, smallImage: _Optional[_Union[WebSmallImage, _Mapping]] = ..., largeImage: _Optional[_Union[WebSmallImage, _Mapping]] = ..., fullImage: _Optional[_Union[WebSmallImage, _Mapping]] = ..., id: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., date: _Optional[_Union[WebInt64Value_1, _Mapping]] = ...) -> None: ...

class WebAvatars(_message.Message):
    __slots__ = ("avatars",)
    AVATARS_FIELD_NUMBER: _ClassVar[int]
    avatars: _containers.RepeatedCompositeFieldContainer[WebAvatar]
    def __init__(self, avatars: _Optional[_Iterable[_Union[WebAvatar, _Mapping]]] = ...) -> None: ...

class WebBalance(_message.Message):
    __slots__ = ("currency", "amount")
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    currency: int
    amount: int
    def __init__(self, currency: _Optional[int] = ..., amount: _Optional[int] = ...) -> None: ...

class WebBankEx(_message.Message):
    __slots__ = ("bankMoneyTransfer", "bankRemain", "bankTransaction", "receiptMessage", "deprecatedReceipt", "deprecatedReceiptMessage")
    BANKMONEYTRANSFER_FIELD_NUMBER: _ClassVar[int]
    BANKREMAIN_FIELD_NUMBER: _ClassVar[int]
    BANKTRANSACTION_FIELD_NUMBER: _ClassVar[int]
    RECEIPTMESSAGE_FIELD_NUMBER: _ClassVar[int]
    DEPRECATEDRECEIPT_FIELD_NUMBER: _ClassVar[int]
    DEPRECATEDRECEIPTMESSAGE_FIELD_NUMBER: _ClassVar[int]
    bankMoneyTransfer: WebBankMoneyTransfer
    bankRemain: WebBankRemain
    bankTransaction: WebBankTransaction
    receiptMessage: WebReceiptMessage
    deprecatedReceipt: WebDeprecatedReceipt
    deprecatedReceiptMessage: WebDeprecatedReceiptMessage
    def __init__(self, bankMoneyTransfer: _Optional[_Union[WebBankMoneyTransfer, _Mapping]] = ..., bankRemain: _Optional[_Union[WebBankRemain, _Mapping]] = ..., bankTransaction: _Optional[_Union[WebBankTransaction, _Mapping]] = ..., receiptMessage: _Optional[_Union[WebReceiptMessage, _Mapping]] = ..., deprecatedReceipt: _Optional[_Union[WebDeprecatedReceipt, _Mapping]] = ..., deprecatedReceiptMessage: _Optional[_Union[WebDeprecatedReceiptMessage, _Mapping]] = ...) -> None: ...

class WebBankMessage(_message.Message):
    __slots__ = ("bankEx",)
    BANKEX_FIELD_NUMBER: _ClassVar[int]
    bankEx: WebBankEx
    def __init__(self, bankEx: _Optional[_Union[WebBankEx, _Mapping]] = ...) -> None: ...

class WebBankMoneyTransfer(_message.Message):
    __slots__ = ("originAccount", "destAccount", "moneyTransferVal", "referenceNumber", "paymentCode", "description", "moneyTransferDate", "branch")
    ORIGINACCOUNT_FIELD_NUMBER: _ClassVar[int]
    DESTACCOUNT_FIELD_NUMBER: _ClassVar[int]
    MONEYTRANSFERVAL_FIELD_NUMBER: _ClassVar[int]
    REFERENCENUMBER_FIELD_NUMBER: _ClassVar[int]
    PAYMENTCODE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MONEYTRANSFERDATE_FIELD_NUMBER: _ClassVar[int]
    BRANCH_FIELD_NUMBER: _ClassVar[int]
    originAccount: WebOriginAccount
    destAccount: WebOriginAccount
    moneyTransferVal: int
    referenceNumber: int
    paymentCode: int
    description: WebStringValue
    moneyTransferDate: int
    branch: WebInt32Value
    def __init__(self, originAccount: _Optional[_Union[WebOriginAccount, _Mapping]] = ..., destAccount: _Optional[_Union[WebOriginAccount, _Mapping]] = ..., moneyTransferVal: _Optional[int] = ..., referenceNumber: _Optional[int] = ..., paymentCode: _Optional[int] = ..., description: _Optional[_Union[WebStringValue, _Mapping]] = ..., moneyTransferDate: _Optional[int] = ..., branch: _Optional[_Union[WebInt32Value, _Mapping]] = ...) -> None: ...

class WebBankRemain(_message.Message):
    __slots__ = ("bankAccount", "remainDate")
    BANKACCOUNT_FIELD_NUMBER: _ClassVar[int]
    REMAINDATE_FIELD_NUMBER: _ClassVar[int]
    bankAccount: WebOriginAccount
    remainDate: int
    def __init__(self, bankAccount: _Optional[_Union[WebOriginAccount, _Mapping]] = ..., remainDate: _Optional[int] = ...) -> None: ...

class WebBankTransaction(_message.Message):
    __slots__ = ("transactions",)
    TRANSACTIONS_FIELD_NUMBER: _ClassVar[int]
    transactions: _containers.RepeatedCompositeFieldContainer[WebT_t6_95053]
    def __init__(self, transactions: _Optional[_Iterable[_Union[WebT_t6_95053, _Mapping]]] = ...) -> None: ...

class WebBannedMessage(_message.Message):
    __slots__ = ("banReason",)
    BANREASON_FIELD_NUMBER: _ClassVar[int]
    banReason: int
    def __init__(self, banReason: _Optional[int] = ...) -> None: ...

class WebBillOrderMessage(_message.Message):
    __slots__ = ("billId", "payId", "amount", "terminalId", "cardAcqId", "billType")
    BILLID_FIELD_NUMBER: _ClassVar[int]
    PAYID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    TERMINALID_FIELD_NUMBER: _ClassVar[int]
    CARDACQID_FIELD_NUMBER: _ClassVar[int]
    BILLTYPE_FIELD_NUMBER: _ClassVar[int]
    billId: str
    payId: str
    amount: int
    terminalId: str
    cardAcqId: str
    billType: int
    def __init__(self, billId: _Optional[str] = ..., payId: _Optional[str] = ..., amount: _Optional[int] = ..., terminalId: _Optional[str] = ..., cardAcqId: _Optional[str] = ..., billType: _Optional[int] = ...) -> None: ...

class WebBinaryMessage(_message.Message):
    __slots__ = ("contentTag", "msg")
    CONTENTTAG_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    contentTag: str
    msg: bytes
    def __init__(self, contentTag: _Optional[str] = ..., msg: _Optional[bytes] = ...) -> None: ...

class WebBoolValue_1(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: bool
    def __init__(self, value: _Optional[bool] = ...) -> None: ...

class WebBot(_message.Message):
    __slots__ = ("type", "id")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    type: int
    id: int
    def __init__(self, type: _Optional[int] = ..., id: _Optional[int] = ...) -> None: ...

class WebBotCommand(_message.Message):
    __slots__ = ("slashCommand", "description", "locKey")
    SLASHCOMMAND_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LOCKEY_FIELD_NUMBER: _ClassVar[int]
    slashCommand: str
    description: str
    locKey: WebStringValue
    def __init__(self, slashCommand: _Optional[str] = ..., description: _Optional[str] = ..., locKey: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebBotExInfo(_message.Message):
    __slots__ = ("botActiveUsers", "hasMainMiniApp", "intro", "introMessage", "hasTimcheProfile", "hasMultipleTopics", "allowTopicCreation")
    BOTACTIVEUSERS_FIELD_NUMBER: _ClassVar[int]
    HASMAINMINIAPP_FIELD_NUMBER: _ClassVar[int]
    INTRO_FIELD_NUMBER: _ClassVar[int]
    INTROMESSAGE_FIELD_NUMBER: _ClassVar[int]
    HASTIMCHEPROFILE_FIELD_NUMBER: _ClassVar[int]
    HASMULTIPLETOPICS_FIELD_NUMBER: _ClassVar[int]
    ALLOWTOPICCREATION_FIELD_NUMBER: _ClassVar[int]
    botActiveUsers: WebStringValue
    hasMainMiniApp: WebBoolValue_1
    intro: WebIntro
    introMessage: WebIntroMessage
    hasTimcheProfile: WebBoolValue_1
    hasMultipleTopics: bool
    allowTopicCreation: bool
    def __init__(self, botActiveUsers: _Optional[_Union[WebStringValue, _Mapping]] = ..., hasMainMiniApp: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., intro: _Optional[_Union[WebIntro, _Mapping]] = ..., introMessage: _Optional[_Union[WebIntroMessage, _Mapping]] = ..., hasTimcheProfile: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., hasMultipleTopics: _Optional[bool] = ..., allowTopicCreation: _Optional[bool] = ...) -> None: ...

class WebBoughtPremiumMessage(_message.Message):
    __slots__ = ("originalMessage",)
    ORIGINALMESSAGE_FIELD_NUMBER: _ClassVar[int]
    originalMessage: WebMessage
    def __init__(self, originalMessage: _Optional[_Union[WebMessage, _Mapping]] = ...) -> None: ...

class WebBtnList(_message.Message):
    __slots__ = ("text", "value", "action")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    text: str
    value: str
    action: int
    def __init__(self, text: _Optional[str] = ..., value: _Optional[str] = ..., action: _Optional[int] = ...) -> None: ...

class WebBytesValue(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: bytes
    def __init__(self, value: _Optional[bytes] = ...) -> None: ...

class WebCall(_message.Message):
    __slots__ = ("id", "token", "room", "url", "video", "createDate", "startDate", "adminUid", "peer", "duration", "discardReason", "isLivekit", "discardServiceMessageRid", "discardServiceMessageDate", "extra", "ext")
    class ExtraEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    class ExtEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    ROOM_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    VIDEO_FIELD_NUMBER: _ClassVar[int]
    CREATEDATE_FIELD_NUMBER: _ClassVar[int]
    STARTDATE_FIELD_NUMBER: _ClassVar[int]
    ADMINUID_FIELD_NUMBER: _ClassVar[int]
    PEER_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    DISCARDREASON_FIELD_NUMBER: _ClassVar[int]
    ISLIVEKIT_FIELD_NUMBER: _ClassVar[int]
    DISCARDSERVICEMESSAGERID_FIELD_NUMBER: _ClassVar[int]
    DISCARDSERVICEMESSAGEDATE_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    id: int
    token: str
    room: str
    url: WebStringValue
    video: bool
    createDate: int
    startDate: int
    adminUid: int
    peer: WebBot
    duration: int
    discardReason: int
    isLivekit: bool
    discardServiceMessageRid: WebInt64Value_1
    discardServiceMessageDate: WebInt64Value_1
    extra: _containers.ScalarMap[str, bytes]
    ext: _containers.ScalarMap[str, bytes]
    def __init__(self, id: _Optional[int] = ..., token: _Optional[str] = ..., room: _Optional[str] = ..., url: _Optional[_Union[WebStringValue, _Mapping]] = ..., video: _Optional[bool] = ..., createDate: _Optional[int] = ..., startDate: _Optional[int] = ..., adminUid: _Optional[int] = ..., peer: _Optional[_Union[WebBot, _Mapping]] = ..., duration: _Optional[int] = ..., discardReason: _Optional[int] = ..., isLivekit: _Optional[bool] = ..., discardServiceMessageRid: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., discardServiceMessageDate: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., extra: _Optional[_Mapping[str, bytes]] = ..., ext: _Optional[_Mapping[str, bytes]] = ...) -> None: ...

class WebCallAccepted(_message.Message):
    __slots__ = ("call", "participants")
    CALL_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    call: WebCall
    participants: _containers.RepeatedCompositeFieldContainer[WebPeer]
    def __init__(self, call: _Optional[_Union[WebCall, _Mapping]] = ..., participants: _Optional[_Iterable[_Union[WebPeer, _Mapping]]] = ...) -> None: ...

class WebCallAction(_message.Message):
    __slots__ = ("callId", "actionTaker", "action")
    CALLID_FIELD_NUMBER: _ClassVar[int]
    ACTIONTAKER_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    callId: int
    actionTaker: WebExPeer
    action: WebAction
    def __init__(self, callId: _Optional[int] = ..., actionTaker: _Optional[_Union[WebExPeer, _Mapping]] = ..., action: _Optional[_Union[WebAction, _Mapping]] = ...) -> None: ...

class WebCallDiscarded(_message.Message):
    __slots__ = ("call", "participants")
    CALL_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    call: WebCall
    participants: _containers.RepeatedCompositeFieldContainer[WebPeer]
    def __init__(self, call: _Optional[_Union[WebCall, _Mapping]] = ..., participants: _Optional[_Iterable[_Union[WebPeer, _Mapping]]] = ...) -> None: ...

class WebCallEvent(_message.Message):
    __slots__ = ("callId", "triggererIdentity", "type", "extraData")
    class ExtraDataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    CALLID_FIELD_NUMBER: _ClassVar[int]
    TRIGGERERIDENTITY_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    EXTRADATA_FIELD_NUMBER: _ClassVar[int]
    callId: int
    triggererIdentity: str
    type: int
    extraData: _containers.ScalarMap[str, bytes]
    def __init__(self, callId: _Optional[int] = ..., triggererIdentity: _Optional[str] = ..., type: _Optional[int] = ..., extraData: _Optional[_Mapping[str, bytes]] = ...) -> None: ...

class WebCallJoinRequestAnswered(_message.Message):
    __slots__ = ("isAllowed", "callId")
    ISALLOWED_FIELD_NUMBER: _ClassVar[int]
    CALLID_FIELD_NUMBER: _ClassVar[int]
    isAllowed: bool
    callId: int
    def __init__(self, isAllowed: _Optional[bool] = ..., callId: _Optional[int] = ...) -> None: ...

class WebCallJoinRequestReceived(_message.Message):
    __slots__ = ("callId", "requesterIdentifier", "name")
    CALLID_FIELD_NUMBER: _ClassVar[int]
    REQUESTERIDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    callId: int
    requesterIdentifier: str
    name: str
    def __init__(self, callId: _Optional[int] = ..., requesterIdentifier: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class WebCallLinkGenerated(_message.Message):
    __slots__ = ("groupCall",)
    GROUPCALL_FIELD_NUMBER: _ClassVar[int]
    groupCall: WebGroupCall
    def __init__(self, groupCall: _Optional[_Union[WebGroupCall, _Mapping]] = ...) -> None: ...

class WebCallReactionSent(_message.Message):
    __slots__ = ("sender", "peer", "reaction")
    SENDER_FIELD_NUMBER: _ClassVar[int]
    PEER_FIELD_NUMBER: _ClassVar[int]
    REACTION_FIELD_NUMBER: _ClassVar[int]
    sender: WebOutPeer
    peer: WebOutPeer
    reaction: str
    def __init__(self, sender: _Optional[_Union[WebOutPeer, _Mapping]] = ..., peer: _Optional[_Union[WebOutPeer, _Mapping]] = ..., reaction: _Optional[str] = ...) -> None: ...

class WebCallReceived(_message.Message):
    __slots__ = ("callId", "participants")
    CALLID_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    callId: int
    participants: _containers.RepeatedCompositeFieldContainer[WebPeer]
    def __init__(self, callId: _Optional[int] = ..., participants: _Optional[_Iterable[_Union[WebPeer, _Mapping]]] = ...) -> None: ...

class WebCallStarted(_message.Message):
    __slots__ = ("call", "participants")
    CALL_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    call: WebCall
    participants: _containers.RepeatedCompositeFieldContainer[WebPeer]
    def __init__(self, call: _Optional[_Union[WebCall, _Mapping]] = ..., participants: _Optional[_Iterable[_Union[WebPeer, _Mapping]]] = ...) -> None: ...

class WebCallUpgraded(_message.Message):
    __slots__ = ("previousMode", "currentMode", "callId")
    PREVIOUSMODE_FIELD_NUMBER: _ClassVar[int]
    CURRENTMODE_FIELD_NUMBER: _ClassVar[int]
    CALLID_FIELD_NUMBER: _ClassVar[int]
    previousMode: int
    currentMode: int
    callId: int
    def __init__(self, previousMode: _Optional[int] = ..., currentMode: _Optional[int] = ..., callId: _Optional[int] = ...) -> None: ...

class WebCardinalityChanged(_message.Message):
    __slots__ = ("peer", "rid", "cardinality", "type")
    PEER_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    CARDINALITY_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    rid: int
    cardinality: int
    type: int
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., rid: _Optional[int] = ..., cardinality: _Optional[int] = ..., type: _Optional[int] = ...) -> None: ...

class WebChannelAdTagIdChanged(_message.Message):
    __slots__ = ("groupId", "channelNativeAdTagId", "channelBannerAdTagId")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    CHANNELNATIVEADTAGID_FIELD_NUMBER: _ClassVar[int]
    CHANNELBANNERADTAGID_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    channelNativeAdTagId: str
    channelBannerAdTagId: str
    def __init__(self, groupId: _Optional[int] = ..., channelNativeAdTagId: _Optional[str] = ..., channelBannerAdTagId: _Optional[str] = ...) -> None: ...

class WebChannelAdvertisementTypeChanged(_message.Message):
    __slots__ = ("groupId", "advertisementType")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    ADVERTISEMENTTYPE_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    advertisementType: int
    def __init__(self, groupId: _Optional[int] = ..., advertisementType: _Optional[int] = ...) -> None: ...

class WebChannelNickChanged(_message.Message):
    __slots__ = ("groupId", "nick")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    NICK_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    nick: str
    def __init__(self, groupId: _Optional[int] = ..., nick: _Optional[str] = ...) -> None: ...

class WebChargeOrderMessage(_message.Message):
    __slots__ = ("providerId", "phoneNo", "amount", "terminalId", "cardAcqId")
    PROVIDERID_FIELD_NUMBER: _ClassVar[int]
    PHONENO_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    TERMINALID_FIELD_NUMBER: _ClassVar[int]
    CARDACQID_FIELD_NUMBER: _ClassVar[int]
    providerId: str
    phoneNo: str
    amount: int
    terminalId: str
    cardAcqId: str
    def __init__(self, providerId: _Optional[str] = ..., phoneNo: _Optional[str] = ..., amount: _Optional[int] = ..., terminalId: _Optional[str] = ..., cardAcqId: _Optional[str] = ...) -> None: ...

class WebChatArchive(_message.Message):
    __slots__ = ("peer",)
    PEER_FIELD_NUMBER: _ClassVar[int]
    IS_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., **kwargs) -> None: ...

class WebChatClear(_message.Message):
    __slots__ = ("peer",)
    PEER_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ...) -> None: ...

class WebChatDelete(_message.Message):
    __slots__ = ("peer",)
    PEER_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ...) -> None: ...

class WebChatFavourite(_message.Message):
    __slots__ = ("peer",)
    PEER_FIELD_NUMBER: _ClassVar[int]
    IS_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., **kwargs) -> None: ...

class WebChatGroupsChanged(_message.Message):
    __slots__ = ("dialogs",)
    DIALOGS_FIELD_NUMBER: _ClassVar[int]
    dialogs: _containers.RepeatedCompositeFieldContainer[WebT_wpU]
    def __init__(self, dialogs: _Optional[_Iterable[_Union[WebT_wpU, _Mapping]]] = ...) -> None: ...

class WebChatShow(_message.Message):
    __slots__ = ("peer",)
    PEER_FIELD_NUMBER: _ClassVar[int]
    IS_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., **kwargs) -> None: ...

class WebChunk(_message.Message):
    __slots__ = ("id", "data")
    ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    id: int
    data: WebT_d_61936
    def __init__(self, id: _Optional[int] = ..., data: _Optional[_Union[WebT_d_61936, _Mapping]] = ...) -> None: ...

class WebCollection(_message.Message):
    __slots__ = ("id", "accessHash", "stickers", "animated", "animatedStickers", "name")
    ID_FIELD_NUMBER: _ClassVar[int]
    ACCESSHASH_FIELD_NUMBER: _ClassVar[int]
    STICKERS_FIELD_NUMBER: _ClassVar[int]
    ANIMATED_FIELD_NUMBER: _ClassVar[int]
    ANIMATEDSTICKERS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: int
    accessHash: int
    stickers: _containers.RepeatedCompositeFieldContainer[WebSticker]
    animated: WebBoolValue_1
    animatedStickers: _containers.RepeatedCompositeFieldContainer[WebAnimatedSticker]
    name: WebStringValue
    def __init__(self, id: _Optional[int] = ..., accessHash: _Optional[int] = ..., stickers: _Optional[_Iterable[_Union[WebSticker, _Mapping]]] = ..., animated: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., animatedStickers: _Optional[_Iterable[_Union[WebAnimatedSticker, _Mapping]]] = ..., name: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebCondition(_message.Message):
    __slots__ = ("exceptedPermissions", "contacts", "query")
    EXCEPTEDPERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    CONTACTS_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    exceptedPermissions: WebBoolValue_1
    contacts: WebBoolValue_1
    query: WebStringValue
    def __init__(self, exceptedPermissions: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., contacts: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., query: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebContactInfo(_message.Message):
    __slots__ = ("type", "stringValue", "longValue", "title", "subtitle", "typeSpec")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STRINGVALUE_FIELD_NUMBER: _ClassVar[int]
    LONGVALUE_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    SUBTITLE_FIELD_NUMBER: _ClassVar[int]
    TYPESPEC_FIELD_NUMBER: _ClassVar[int]
    type: int
    stringValue: WebStringValue
    longValue: WebInt64Value_1
    title: WebStringValue
    subtitle: WebStringValue
    typeSpec: WebStringValue
    def __init__(self, type: _Optional[int] = ..., stringValue: _Optional[_Union[WebStringValue, _Mapping]] = ..., longValue: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., title: _Optional[_Union[WebStringValue, _Mapping]] = ..., subtitle: _Optional[_Union[WebStringValue, _Mapping]] = ..., typeSpec: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebContactRegistered(_message.Message):
    __slots__ = ("uid", "isSilent", "date", "rid")
    UID_FIELD_NUMBER: _ClassVar[int]
    ISSILENT_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    uid: int
    isSilent: bool
    date: int
    rid: int
    def __init__(self, uid: _Optional[int] = ..., isSilent: _Optional[bool] = ..., date: _Optional[int] = ..., rid: _Optional[int] = ...) -> None: ...

class WebContactsAdded(_message.Message):
    __slots__ = ("uids", "phones")
    UIDS_FIELD_NUMBER: _ClassVar[int]
    PHONES_FIELD_NUMBER: _ClassVar[int]
    uids: _containers.RepeatedScalarFieldContainer[int]
    phones: WebExt
    def __init__(self, uids: _Optional[_Iterable[int]] = ..., phones: _Optional[_Union[WebExt, _Mapping]] = ...) -> None: ...

class WebContactsRemoved(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebCopyText(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class WebCrowdFundingMessage(_message.Message):
    __slots__ = ("totalAmount", "cardNumber", "sliceAmount", "title", "description", "endDate", "status", "photo", "openWebView")
    TOTALAMOUNT_FIELD_NUMBER: _ClassVar[int]
    CARDNUMBER_FIELD_NUMBER: _ClassVar[int]
    SLICEAMOUNT_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ENDDATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PHOTO_FIELD_NUMBER: _ClassVar[int]
    OPENWEBVIEW_FIELD_NUMBER: _ClassVar[int]
    totalAmount: int
    cardNumber: str
    sliceAmount: int
    title: str
    description: str
    endDate: int
    status: int
    photo: WebMedia
    openWebView: bool
    def __init__(self, totalAmount: _Optional[int] = ..., cardNumber: _Optional[str] = ..., sliceAmount: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., endDate: _Optional[int] = ..., status: _Optional[int] = ..., photo: _Optional[_Union[WebMedia, _Mapping]] = ..., openWebView: _Optional[bool] = ...) -> None: ...

class WebCustomAction(_message.Message):
    __slots__ = ("id", "type")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: WebType
    def __init__(self, id: _Optional[str] = ..., type: _Optional[_Union[WebType, _Mapping]] = ...) -> None: ...

class WebCustomDoNothingAction(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebCustomOpenUrlAction(_message.Message):
    __slots__ = ("url", "buttonTitle", "shouldSearchInternal")
    URL_FIELD_NUMBER: _ClassVar[int]
    BUTTONTITLE_FIELD_NUMBER: _ClassVar[int]
    SHOULDSEARCHINTERNAL_FIELD_NUMBER: _ClassVar[int]
    url: str
    buttonTitle: str
    shouldSearchInternal: bool
    def __init__(self, url: _Optional[str] = ..., buttonTitle: _Optional[str] = ..., shouldSearchInternal: _Optional[bool] = ...) -> None: ...

class WebDates(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebDeletedMessage(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebDeleteMessageRequest(_message.Message):
    __slots__ = ("peer", "rids", "dates", "justMine")
    PEER_FIELD_NUMBER: _ClassVar[int]
    RIDS_FIELD_NUMBER: _ClassVar[int]
    DATES_FIELD_NUMBER: _ClassVar[int]
    JUSTMINE_FIELD_NUMBER: _ClassVar[int]
    peer: WebPeer
    rids: _containers.RepeatedScalarFieldContainer[int]
    dates: WebT_LWL
    justMine: WebBoolValue_1
    def __init__(self, peer: _Optional[_Union[WebPeer, _Mapping]] = ..., rids: _Optional[_Iterable[int]] = ..., dates: _Optional[_Union[WebT_LWL, _Mapping]] = ..., justMine: _Optional[_Union[WebBoolValue_1, _Mapping]] = ...) -> None: ...

class WebDeprecatedReceipt(_message.Message):
    __slots__ = ("originalMessage", "receiptType", "transferInfo")
    class TransferInfoEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    ORIGINALMESSAGE_FIELD_NUMBER: _ClassVar[int]
    RECEIPTTYPE_FIELD_NUMBER: _ClassVar[int]
    TRANSFERINFO_FIELD_NUMBER: _ClassVar[int]
    originalMessage: WebMessage
    receiptType: int
    transferInfo: _containers.ScalarMap[str, bytes]
    def __init__(self, originalMessage: _Optional[_Union[WebMessage, _Mapping]] = ..., receiptType: _Optional[int] = ..., transferInfo: _Optional[_Mapping[str, bytes]] = ...) -> None: ...

class WebDeprecatedReceiptMessage(_message.Message):
    __slots__ = ("orginalMessage", "receiptType", "transferInfo", "orginalMessageRid", "orginalMessageUid")
    class TransferInfoEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    ORGINALMESSAGE_FIELD_NUMBER: _ClassVar[int]
    RECEIPTTYPE_FIELD_NUMBER: _ClassVar[int]
    TRANSFERINFO_FIELD_NUMBER: _ClassVar[int]
    ORGINALMESSAGERID_FIELD_NUMBER: _ClassVar[int]
    ORGINALMESSAGEUID_FIELD_NUMBER: _ClassVar[int]
    orginalMessage: WebMessage
    receiptType: int
    transferInfo: _containers.ScalarMap[str, bytes]
    orginalMessageRid: WebInt64Value_1
    orginalMessageUid: WebStringValue
    def __init__(self, orginalMessage: _Optional[_Union[WebMessage, _Mapping]] = ..., receiptType: _Optional[int] = ..., transferInfo: _Optional[_Mapping[str, bytes]] = ..., orginalMessageRid: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., orginalMessageUid: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebDialog(_message.Message):
    __slots__ = ("peer", "unreadCount", "sortDate", "senderUid", "rid", "date", "message", "state", "firstUnreadDate", "attributes", "exInfo", "isMessageForwarded", "unreadMentions", "unreadReactions", "markedAsUnread", "isMute")
    PEER_FIELD_NUMBER: _ClassVar[int]
    UNREADCOUNT_FIELD_NUMBER: _ClassVar[int]
    SORTDATE_FIELD_NUMBER: _ClassVar[int]
    SENDERUID_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    FIRSTUNREADDATE_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    EXINFO_FIELD_NUMBER: _ClassVar[int]
    ISMESSAGEFORWARDED_FIELD_NUMBER: _ClassVar[int]
    UNREADMENTIONS_FIELD_NUMBER: _ClassVar[int]
    UNREADREACTIONS_FIELD_NUMBER: _ClassVar[int]
    MARKEDASUNREAD_FIELD_NUMBER: _ClassVar[int]
    ISMUTE_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    unreadCount: int
    sortDate: int
    senderUid: int
    rid: int
    date: int
    message: WebMessage
    state: int
    firstUnreadDate: WebInt64Value_1
    attributes: WebAttributes
    exInfo: WebExInfo
    isMessageForwarded: bool
    unreadMentions: _containers.RepeatedCompositeFieldContainer[WebMessageId]
    unreadReactions: _containers.RepeatedCompositeFieldContainer[WebMessageId]
    markedAsUnread: bool
    isMute: bool
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., unreadCount: _Optional[int] = ..., sortDate: _Optional[int] = ..., senderUid: _Optional[int] = ..., rid: _Optional[int] = ..., date: _Optional[int] = ..., message: _Optional[_Union[WebMessage, _Mapping]] = ..., state: _Optional[int] = ..., firstUnreadDate: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., attributes: _Optional[_Union[WebAttributes, _Mapping]] = ..., exInfo: _Optional[_Union[WebExInfo, _Mapping]] = ..., isMessageForwarded: _Optional[bool] = ..., unreadMentions: _Optional[_Iterable[_Union[WebMessageId, _Mapping]]] = ..., unreadReactions: _Optional[_Iterable[_Union[WebMessageId, _Mapping]]] = ..., markedAsUnread: _Optional[bool] = ..., isMute: _Optional[bool] = ...) -> None: ...

class WebDialogArchiveStatus(_message.Message):
    __slots__ = ("exPeers", "isArchived")
    EXPEERS_FIELD_NUMBER: _ClassVar[int]
    ISARCHIVED_FIELD_NUMBER: _ClassVar[int]
    exPeers: _containers.RepeatedCompositeFieldContainer[WebExPeer]
    isArchived: bool
    def __init__(self, exPeers: _Optional[_Iterable[_Union[WebExPeer, _Mapping]]] = ..., isArchived: _Optional[bool] = ...) -> None: ...

class WebDialogsMarkedAsRead(_message.Message):
    __slots__ = ("peers",)
    PEERS_FIELD_NUMBER: _ClassVar[int]
    peers: _containers.RepeatedCompositeFieldContainer[WebExPeer]
    def __init__(self, peers: _Optional[_Iterable[_Union[WebExPeer, _Mapping]]] = ...) -> None: ...

class WebDialogsMarkedAsUnread(_message.Message):
    __slots__ = ("peers",)
    PEERS_FIELD_NUMBER: _ClassVar[int]
    peers: _containers.RepeatedCompositeFieldContainer[WebExPeer]
    def __init__(self, peers: _Optional[_Iterable[_Union[WebExPeer, _Mapping]]] = ...) -> None: ...

class WebDialogsUnpinned(_message.Message):
    __slots__ = ("folderId", "unpinnedPeers")
    FOLDERID_FIELD_NUMBER: _ClassVar[int]
    UNPINNEDPEERS_FIELD_NUMBER: _ClassVar[int]
    folderId: int
    unpinnedPeers: _containers.RepeatedCompositeFieldContainer[WebExPeer]
    def __init__(self, folderId: _Optional[int] = ..., unpinnedPeers: _Optional[_Iterable[_Union[WebExPeer, _Mapping]]] = ...) -> None: ...

class WebDocumentExAudio(_message.Message):
    __slots__ = ("duration", "album", "artist", "genre", "track", "cover")
    DURATION_FIELD_NUMBER: _ClassVar[int]
    ALBUM_FIELD_NUMBER: _ClassVar[int]
    ARTIST_FIELD_NUMBER: _ClassVar[int]
    GENRE_FIELD_NUMBER: _ClassVar[int]
    TRACK_FIELD_NUMBER: _ClassVar[int]
    COVER_FIELD_NUMBER: _ClassVar[int]
    duration: int
    album: str
    artist: str
    genre: str
    track: str
    cover: WebBytesValue
    def __init__(self, duration: _Optional[int] = ..., album: _Optional[str] = ..., artist: _Optional[str] = ..., genre: _Optional[str] = ..., track: _Optional[str] = ..., cover: _Optional[_Union[WebBytesValue, _Mapping]] = ...) -> None: ...

class WebDocumentExGif(_message.Message):
    __slots__ = ("w", "h", "duration")
    W_FIELD_NUMBER: _ClassVar[int]
    H_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    w: int
    h: int
    duration: int
    def __init__(self, w: _Optional[int] = ..., h: _Optional[int] = ..., duration: _Optional[int] = ...) -> None: ...

class WebDocumentExPhoto(_message.Message):
    __slots__ = ("w", "h")
    W_FIELD_NUMBER: _ClassVar[int]
    H_FIELD_NUMBER: _ClassVar[int]
    w: int
    h: int
    def __init__(self, w: _Optional[int] = ..., h: _Optional[int] = ...) -> None: ...

class WebDocumentExVideo(_message.Message):
    __slots__ = ("w", "h", "duration")
    W_FIELD_NUMBER: _ClassVar[int]
    H_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    w: int
    h: int
    duration: int
    def __init__(self, w: _Optional[int] = ..., h: _Optional[int] = ..., duration: _Optional[int] = ...) -> None: ...

class WebDocumentExVoice(_message.Message):
    __slots__ = ("duration", "transcript")
    DURATION_FIELD_NUMBER: _ClassVar[int]
    TRANSCRIPT_FIELD_NUMBER: _ClassVar[int]
    duration: int
    transcript: WebStringValue
    def __init__(self, duration: _Optional[int] = ..., transcript: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebDoNothingAction(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebDownloadSource(_message.Message):
    __slots__ = ("documentMessage",)
    DOCUMENTMESSAGE_FIELD_NUMBER: _ClassVar[int]
    documentMessage: WebMedia
    def __init__(self, documentMessage: _Optional[_Union[WebMedia, _Mapping]] = ...) -> None: ...

class WebEmptyMessage(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebEmptyUpdate(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebEndLive(_message.Message):
    __slots__ = ("info",)
    INFO_FIELD_NUMBER: _ClassVar[int]
    info: WebInfo
    def __init__(self, info: _Optional[_Union[WebInfo, _Mapping]] = ...) -> None: ...

class WebEndpoint(_message.Message):
    __slots__ = ("id", "host", "port", "tlsPublicKeyHash", "knownIp", "type")
    ID_FIELD_NUMBER: _ClassVar[int]
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    TLSPUBLICKEYHASH_FIELD_NUMBER: _ClassVar[int]
    KNOWNIP_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    id: int
    host: str
    port: int
    tlsPublicKeyHash: _containers.RepeatedScalarFieldContainer[str]
    knownIp: str
    type: int
    def __init__(self, id: _Optional[int] = ..., host: _Optional[str] = ..., port: _Optional[int] = ..., tlsPublicKeyHash: _Optional[_Iterable[str]] = ..., knownIp: _Optional[str] = ..., type: _Optional[int] = ...) -> None: ...

class WebEndpointChanged(_message.Message):
    __slots__ = ("endpoints",)
    ENDPOINTS_FIELD_NUMBER: _ClassVar[int]
    endpoints: _containers.RepeatedCompositeFieldContainer[WebEndpoint]
    def __init__(self, endpoints: _Optional[_Iterable[_Union[WebEndpoint, _Mapping]]] = ...) -> None: ...

class WebError(_message.Message):
    __slots__ = ("code", "message", "details")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    details: WebExt
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., details: _Optional[_Union[WebExt, _Mapping]] = ...) -> None: ...

class WebExInfo(_message.Message):
    __slots__ = ("exPeerType", "peerIdentity", "peerCategory")
    EXPEERTYPE_FIELD_NUMBER: _ClassVar[int]
    PEERIDENTITY_FIELD_NUMBER: _ClassVar[int]
    PEERCATEGORY_FIELD_NUMBER: _ClassVar[int]
    exPeerType: int
    peerIdentity: int
    peerCategory: WebStringValue
    def __init__(self, exPeerType: _Optional[int] = ..., peerIdentity: _Optional[int] = ..., peerCategory: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebExInfoAddress(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: int
    value: str
    def __init__(self, key: _Optional[int] = ..., value: _Optional[str] = ...) -> None: ...

class WebExPeer(_message.Message):
    __slots__ = ("type", "id", "accessHash")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    ACCESSHASH_FIELD_NUMBER: _ClassVar[int]
    type: int
    id: int
    accessHash: int
    def __init__(self, type: _Optional[int] = ..., id: _Optional[int] = ..., accessHash: _Optional[int] = ...) -> None: ...

class WebExt(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[WebT_d_46216]
    def __init__(self, items: _Optional[_Iterable[_Union[WebT_d_46216, _Mapping]]] = ...) -> None: ...

class WebField(_message.Message):
    __slots__ = ("title", "value", "isShort")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    ISSHORT_FIELD_NUMBER: _ClassVar[int]
    title: str
    value: str
    isShort: WebBoolValue_1
    def __init__(self, title: _Optional[str] = ..., value: _Optional[str] = ..., isShort: _Optional[_Union[WebBoolValue_1, _Mapping]] = ...) -> None: ...

class WebFileLocation(_message.Message):
    __slots__ = ("fileId", "accessHash", "fileStorageVersion")
    FILEID_FIELD_NUMBER: _ClassVar[int]
    ACCESSHASH_FIELD_NUMBER: _ClassVar[int]
    FILESTORAGEVERSION_FIELD_NUMBER: _ClassVar[int]
    fileId: int
    accessHash: int
    fileStorageVersion: WebInt32Value
    def __init__(self, fileId: _Optional[int] = ..., accessHash: _Optional[int] = ..., fileStorageVersion: _Optional[_Union[WebInt32Value, _Mapping]] = ...) -> None: ...

class WebFileUrl(_message.Message):
    __slots__ = ("fileId", "url", "timeout", "unsignedUrl", "unsignedUrlHeaders", "chunkSize")
    FILEID_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    UNSIGNEDURL_FIELD_NUMBER: _ClassVar[int]
    UNSIGNEDURLHEADERS_FIELD_NUMBER: _ClassVar[int]
    CHUNKSIZE_FIELD_NUMBER: _ClassVar[int]
    fileId: int
    url: str
    timeout: int
    unsignedUrl: WebStringValue
    unsignedUrlHeaders: _containers.RepeatedCompositeFieldContainer[WebUnsignedUrlHeader]
    chunkSize: WebInt32Value
    def __init__(self, fileId: _Optional[int] = ..., url: _Optional[str] = ..., timeout: _Optional[int] = ..., unsignedUrl: _Optional[_Union[WebStringValue, _Mapping]] = ..., unsignedUrlHeaders: _Optional[_Iterable[_Union[WebUnsignedUrlHeader, _Mapping]]] = ..., chunkSize: _Optional[_Union[WebInt32Value, _Mapping]] = ...) -> None: ...

class WebFilter(_message.Message):
    __slots__ = ("filterOwner", "filterAdmin", "filterGroupType", "filterRestriction", "filterMembersCount")
    FILTEROWNER_FIELD_NUMBER: _ClassVar[int]
    FILTERADMIN_FIELD_NUMBER: _ClassVar[int]
    FILTERGROUPTYPE_FIELD_NUMBER: _ClassVar[int]
    FILTERRESTRICTION_FIELD_NUMBER: _ClassVar[int]
    FILTERMEMBERSCOUNT_FIELD_NUMBER: _ClassVar[int]
    filterOwner: WebFilterOwner
    filterAdmin: WebFilterAdmin
    filterGroupType: WebFilterGroupType
    filterRestriction: WebFilterRestriction
    filterMembersCount: WebFilterMembersCount
    def __init__(self, filterOwner: _Optional[_Union[WebFilterOwner, _Mapping]] = ..., filterAdmin: _Optional[_Union[WebFilterAdmin, _Mapping]] = ..., filterGroupType: _Optional[_Union[WebFilterGroupType, _Mapping]] = ..., filterRestriction: _Optional[_Union[WebFilterRestriction, _Mapping]] = ..., filterMembersCount: _Optional[_Union[WebFilterMembersCount, _Mapping]] = ...) -> None: ...

class WebFilterAdmin(_message.Message):
    __slots__ = ("isAdmin",)
    ISADMIN_FIELD_NUMBER: _ClassVar[int]
    isAdmin: bool
    def __init__(self, isAdmin: _Optional[bool] = ...) -> None: ...

class WebFilterGroupType(_message.Message):
    __slots__ = ("groupType",)
    GROUPTYPE_FIELD_NUMBER: _ClassVar[int]
    groupType: int
    def __init__(self, groupType: _Optional[int] = ...) -> None: ...

class WebFilterMembersCount(_message.Message):
    __slots__ = ("minCount",)
    MINCOUNT_FIELD_NUMBER: _ClassVar[int]
    minCount: int
    def __init__(self, minCount: _Optional[int] = ...) -> None: ...

class WebFilterOwner(_message.Message):
    __slots__ = ("isOwner",)
    ISOWNER_FIELD_NUMBER: _ClassVar[int]
    isOwner: bool
    def __init__(self, isOwner: _Optional[bool] = ...) -> None: ...

class WebFilterRestriction(_message.Message):
    __slots__ = ("restriction",)
    RESTRICTION_FIELD_NUMBER: _ClassVar[int]
    restriction: int
    def __init__(self, restriction: _Optional[int] = ...) -> None: ...

class WebFolder(_message.Message):
    __slots__ = ("id", "name", "peers", "unreadPeers", "isReserved")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PEERS_FIELD_NUMBER: _ClassVar[int]
    UNREADPEERS_FIELD_NUMBER: _ClassVar[int]
    ISRESERVED_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    peers: _containers.RepeatedCompositeFieldContainer[WebExPeer]
    unreadPeers: _containers.RepeatedCompositeFieldContainer[WebExPeer]
    isReserved: bool
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., peers: _Optional[_Iterable[_Union[WebExPeer, _Mapping]]] = ..., unreadPeers: _Optional[_Iterable[_Union[WebExPeer, _Mapping]]] = ..., isReserved: _Optional[bool] = ...) -> None: ...

class WebFolderCreated(_message.Message):
    __slots__ = ("folder", "index")
    FOLDER_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    folder: WebFolder
    index: int
    def __init__(self, folder: _Optional[_Union[WebFolder, _Mapping]] = ..., index: _Optional[int] = ...) -> None: ...

class WebFolderDeleted(_message.Message):
    __slots__ = ("folderId",)
    FOLDERID_FIELD_NUMBER: _ClassVar[int]
    folderId: int
    def __init__(self, folderId: _Optional[int] = ...) -> None: ...

class WebFolderEdited(_message.Message):
    __slots__ = ("folderId", "newName", "addedPeers", "deletedPeers", "unreadPeers")
    FOLDERID_FIELD_NUMBER: _ClassVar[int]
    NEWNAME_FIELD_NUMBER: _ClassVar[int]
    ADDEDPEERS_FIELD_NUMBER: _ClassVar[int]
    DELETEDPEERS_FIELD_NUMBER: _ClassVar[int]
    UNREADPEERS_FIELD_NUMBER: _ClassVar[int]
    folderId: int
    newName: WebStringValue
    addedPeers: _containers.RepeatedCompositeFieldContainer[WebExPeer]
    deletedPeers: _containers.RepeatedCompositeFieldContainer[WebExPeer]
    unreadPeers: _containers.RepeatedCompositeFieldContainer[WebExPeer]
    def __init__(self, folderId: _Optional[int] = ..., newName: _Optional[_Union[WebStringValue, _Mapping]] = ..., addedPeers: _Optional[_Iterable[_Union[WebExPeer, _Mapping]]] = ..., deletedPeers: _Optional[_Iterable[_Union[WebExPeer, _Mapping]]] = ..., unreadPeers: _Optional[_Iterable[_Union[WebExPeer, _Mapping]]] = ...) -> None: ...

class WebFoldersReordered(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebForceClearCache(_message.Message):
    __slots__ = ("backupOptions",)
    BACKUPOPTIONS_FIELD_NUMBER: _ClassVar[int]
    backupOptions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, backupOptions: _Optional[_Iterable[str]] = ...) -> None: ...

class WebFullGroup(_message.Message):
    __slots__ = ("id", "accessHash", "title", "avatar", "ownerUid", "createDate", "groupType", "isMember", "ext", "membersCount", "nick", "becameOrphaned", "permissions", "defaultPermissions", "theme", "about", "members", "exInfo", "pin", "restriction", "advertisementType", "channelNativeAdTagId", "channelBannerAdTagId", "availableReactions", "isSuspend", "linkedGroupPeerId", "discussionGroupEnabled", "privacyBarMode")
    ID_FIELD_NUMBER: _ClassVar[int]
    ACCESSHASH_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AVATAR_FIELD_NUMBER: _ClassVar[int]
    OWNERUID_FIELD_NUMBER: _ClassVar[int]
    CREATEDATE_FIELD_NUMBER: _ClassVar[int]
    GROUPTYPE_FIELD_NUMBER: _ClassVar[int]
    ISMEMBER_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    MEMBERSCOUNT_FIELD_NUMBER: _ClassVar[int]
    NICK_FIELD_NUMBER: _ClassVar[int]
    BECAMEORPHANED_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    DEFAULTPERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    THEME_FIELD_NUMBER: _ClassVar[int]
    ABOUT_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    EXINFO_FIELD_NUMBER: _ClassVar[int]
    PIN_FIELD_NUMBER: _ClassVar[int]
    RESTRICTION_FIELD_NUMBER: _ClassVar[int]
    ADVERTISEMENTTYPE_FIELD_NUMBER: _ClassVar[int]
    CHANNELNATIVEADTAGID_FIELD_NUMBER: _ClassVar[int]
    CHANNELBANNERADTAGID_FIELD_NUMBER: _ClassVar[int]
    AVAILABLEREACTIONS_FIELD_NUMBER: _ClassVar[int]
    ISSUSPEND_FIELD_NUMBER: _ClassVar[int]
    LINKEDGROUPPEERID_FIELD_NUMBER: _ClassVar[int]
    DISCUSSIONGROUPENABLED_FIELD_NUMBER: _ClassVar[int]
    PRIVACYBARMODE_FIELD_NUMBER: _ClassVar[int]
    id: int
    accessHash: int
    title: str
    avatar: WebAvatar
    ownerUid: int
    createDate: int
    groupType: int
    isMember: WebBoolValue_1
    ext: WebExt
    membersCount: WebInt32Value
    nick: WebStringValue
    becameOrphaned: WebBoolValue_1
    permissions: WebPermissions
    defaultPermissions: WebPermissions
    theme: WebStringValue
    about: WebStringValue
    members: _containers.RepeatedCompositeFieldContainer[WebMember]
    exInfo: WebExInfo
    pin: WebHistory
    restriction: int
    advertisementType: int
    channelNativeAdTagId: WebStringValue
    channelBannerAdTagId: WebStringValue
    availableReactions: _containers.RepeatedScalarFieldContainer[str]
    isSuspend: WebBoolValue_1
    linkedGroupPeerId: WebInt32Value
    discussionGroupEnabled: WebBoolValue_1
    privacyBarMode: int
    def __init__(self, id: _Optional[int] = ..., accessHash: _Optional[int] = ..., title: _Optional[str] = ..., avatar: _Optional[_Union[WebAvatar, _Mapping]] = ..., ownerUid: _Optional[int] = ..., createDate: _Optional[int] = ..., groupType: _Optional[int] = ..., isMember: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., ext: _Optional[_Union[WebExt, _Mapping]] = ..., membersCount: _Optional[_Union[WebInt32Value, _Mapping]] = ..., nick: _Optional[_Union[WebStringValue, _Mapping]] = ..., becameOrphaned: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., permissions: _Optional[_Union[WebPermissions, _Mapping]] = ..., defaultPermissions: _Optional[_Union[WebPermissions, _Mapping]] = ..., theme: _Optional[_Union[WebStringValue, _Mapping]] = ..., about: _Optional[_Union[WebStringValue, _Mapping]] = ..., members: _Optional[_Iterable[_Union[WebMember, _Mapping]]] = ..., exInfo: _Optional[_Union[WebExInfo, _Mapping]] = ..., pin: _Optional[_Union[WebHistory, _Mapping]] = ..., restriction: _Optional[int] = ..., advertisementType: _Optional[int] = ..., channelNativeAdTagId: _Optional[_Union[WebStringValue, _Mapping]] = ..., channelBannerAdTagId: _Optional[_Union[WebStringValue, _Mapping]] = ..., availableReactions: _Optional[_Iterable[str]] = ..., isSuspend: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., linkedGroupPeerId: _Optional[_Union[WebInt32Value, _Mapping]] = ..., discussionGroupEnabled: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., privacyBarMode: _Optional[int] = ...) -> None: ...

class WebGeneralNotificationMessage(_message.Message):
    __slots__ = ("title", "description", "action")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    title: str
    description: str
    action: WebT_f_68220
    def __init__(self, title: _Optional[str] = ..., description: _Optional[str] = ..., action: _Optional[_Union[WebT_f_68220, _Mapping]] = ...) -> None: ...

class WebGiftPacketMessage(_message.Message):
    __slots__ = ("giftCount", "totalAmount", "givingType", "walletId", "regarding", "ownerUserId", "coverId", "showTotalAmount")
    GIFTCOUNT_FIELD_NUMBER: _ClassVar[int]
    TOTALAMOUNT_FIELD_NUMBER: _ClassVar[int]
    GIVINGTYPE_FIELD_NUMBER: _ClassVar[int]
    WALLETID_FIELD_NUMBER: _ClassVar[int]
    REGARDING_FIELD_NUMBER: _ClassVar[int]
    OWNERUSERID_FIELD_NUMBER: _ClassVar[int]
    COVERID_FIELD_NUMBER: _ClassVar[int]
    SHOWTOTALAMOUNT_FIELD_NUMBER: _ClassVar[int]
    giftCount: int
    totalAmount: int
    givingType: int
    walletId: WebStringValue
    regarding: WebStringValue
    ownerUserId: int
    coverId: WebInt32Value
    showTotalAmount: WebBoolValue_1
    def __init__(self, giftCount: _Optional[int] = ..., totalAmount: _Optional[int] = ..., givingType: _Optional[int] = ..., walletId: _Optional[_Union[WebStringValue, _Mapping]] = ..., regarding: _Optional[_Union[WebStringValue, _Mapping]] = ..., ownerUserId: _Optional[int] = ..., coverId: _Optional[_Union[WebInt32Value, _Mapping]] = ..., showTotalAmount: _Optional[_Union[WebBoolValue_1, _Mapping]] = ...) -> None: ...

class WebGoldGiftPacketMessage(_message.Message):
    __slots__ = ("id", "amount", "count", "description", "givingType")
    ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    GIVINGTYPE_FIELD_NUMBER: _ClassVar[int]
    id: int
    amount: int
    count: int
    description: str
    givingType: int
    def __init__(self, id: _Optional[int] = ..., amount: _Optional[int] = ..., count: _Optional[int] = ..., description: _Optional[str] = ..., givingType: _Optional[int] = ...) -> None: ...

class WebGroup(_message.Message):
    __slots__ = ("id", "accessHash", "title", "avatar", "isMember", "isHidden", "ext", "groupType", "canSendMessage", "nick", "becameOrphaned", "stateVersion", "membersCount", "permissions", "defaultPermissions", "ownerUid", "availableReactions", "isSuspend", "exInfo", "linkedGroupPeerId", "discussionGroupEnabled", "restriction")
    ID_FIELD_NUMBER: _ClassVar[int]
    ACCESSHASH_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AVATAR_FIELD_NUMBER: _ClassVar[int]
    ISMEMBER_FIELD_NUMBER: _ClassVar[int]
    ISHIDDEN_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    GROUPTYPE_FIELD_NUMBER: _ClassVar[int]
    CANSENDMESSAGE_FIELD_NUMBER: _ClassVar[int]
    NICK_FIELD_NUMBER: _ClassVar[int]
    BECAMEORPHANED_FIELD_NUMBER: _ClassVar[int]
    STATEVERSION_FIELD_NUMBER: _ClassVar[int]
    MEMBERSCOUNT_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    DEFAULTPERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    OWNERUID_FIELD_NUMBER: _ClassVar[int]
    AVAILABLEREACTIONS_FIELD_NUMBER: _ClassVar[int]
    ISSUSPEND_FIELD_NUMBER: _ClassVar[int]
    EXINFO_FIELD_NUMBER: _ClassVar[int]
    LINKEDGROUPPEERID_FIELD_NUMBER: _ClassVar[int]
    DISCUSSIONGROUPENABLED_FIELD_NUMBER: _ClassVar[int]
    RESTRICTION_FIELD_NUMBER: _ClassVar[int]
    id: int
    accessHash: int
    title: str
    avatar: WebAvatar
    isMember: WebBoolValue_1
    isHidden: WebBoolValue_1
    ext: WebExt
    groupType: int
    canSendMessage: WebBoolValue_1
    nick: WebStringValue
    becameOrphaned: WebBoolValue_1
    stateVersion: WebInt64Value_1
    membersCount: WebInt32Value
    permissions: WebPermissions
    defaultPermissions: WebPermissions
    ownerUid: WebInt32Value
    availableReactions: _containers.RepeatedScalarFieldContainer[str]
    isSuspend: WebBoolValue_1
    exInfo: WebExInfo
    linkedGroupPeerId: WebInt32Value
    discussionGroupEnabled: WebBoolValue_1
    restriction: int
    def __init__(self, id: _Optional[int] = ..., accessHash: _Optional[int] = ..., title: _Optional[str] = ..., avatar: _Optional[_Union[WebAvatar, _Mapping]] = ..., isMember: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., isHidden: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., ext: _Optional[_Union[WebExt, _Mapping]] = ..., groupType: _Optional[int] = ..., canSendMessage: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., nick: _Optional[_Union[WebStringValue, _Mapping]] = ..., becameOrphaned: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., stateVersion: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., membersCount: _Optional[_Union[WebInt32Value, _Mapping]] = ..., permissions: _Optional[_Union[WebPermissions, _Mapping]] = ..., defaultPermissions: _Optional[_Union[WebPermissions, _Mapping]] = ..., ownerUid: _Optional[_Union[WebInt32Value, _Mapping]] = ..., availableReactions: _Optional[_Iterable[str]] = ..., isSuspend: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., exInfo: _Optional[_Union[WebExInfo, _Mapping]] = ..., linkedGroupPeerId: _Optional[_Union[WebInt32Value, _Mapping]] = ..., discussionGroupEnabled: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., restriction: _Optional[int] = ...) -> None: ...

class WebGroupAboutChanged(_message.Message):
    __slots__ = ("groupId", "about")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    ABOUT_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    about: WebStringValue
    def __init__(self, groupId: _Optional[int] = ..., about: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebGroupAboutChangedObsolete(_message.Message):
    __slots__ = ("groupId", "about")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    ABOUT_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    about: WebStringValue
    def __init__(self, groupId: _Optional[int] = ..., about: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebGroupAvatarChanged(_message.Message):
    __slots__ = ("groupId", "avatar", "avatars")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    AVATAR_FIELD_NUMBER: _ClassVar[int]
    AVATARS_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    avatar: WebAvatar
    avatars: WebAvatars
    def __init__(self, groupId: _Optional[int] = ..., avatar: _Optional[_Union[WebAvatar, _Mapping]] = ..., avatars: _Optional[_Union[WebAvatars, _Mapping]] = ...) -> None: ...

class WebGroupAvatarChangedObsolete(_message.Message):
    __slots__ = ("groupId", "uid", "avatar", "date", "rid")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    AVATAR_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    uid: int
    avatar: WebAvatar
    date: int
    rid: int
    def __init__(self, groupId: _Optional[int] = ..., uid: _Optional[int] = ..., avatar: _Optional[_Union[WebAvatar, _Mapping]] = ..., date: _Optional[int] = ..., rid: _Optional[int] = ...) -> None: ...

class WebGroupBecameOrphaned(_message.Message):
    __slots__ = ("groupId",)
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    def __init__(self, groupId: _Optional[int] = ...) -> None: ...

class WebGroupCall(_message.Message):
    __slots__ = ("id", "room", "token", "url", "video", "createDate", "duration", "initiatorUserId", "peer", "ext", "mode", "link", "isPublic", "extra", "title", "inCallParticipants", "endDate", "pendingRequests", "raisedHandsUserIdentities")
    class ExtEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    class ExtraEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    ROOM_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    VIDEO_FIELD_NUMBER: _ClassVar[int]
    CREATEDATE_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    INITIATORUSERID_FIELD_NUMBER: _ClassVar[int]
    PEER_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    LINK_FIELD_NUMBER: _ClassVar[int]
    ISPUBLIC_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    INCALLPARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    ENDDATE_FIELD_NUMBER: _ClassVar[int]
    PENDINGREQUESTS_FIELD_NUMBER: _ClassVar[int]
    RAISEDHANDSUSERIDENTITIES_FIELD_NUMBER: _ClassVar[int]
    id: int
    room: str
    token: str
    url: WebOffset
    video: bool
    createDate: WebInt64Value_1
    duration: WebInt32Value_1
    initiatorUserId: int
    peer: WebOutPeer
    ext: _containers.ScalarMap[str, bytes]
    mode: int
    link: str
    isPublic: bool
    extra: _containers.ScalarMap[str, bytes]
    title: str
    inCallParticipants: _containers.RepeatedCompositeFieldContainer[WebOutPeer]
    endDate: WebInt64Value_1
    pendingRequests: _containers.RepeatedCompositeFieldContainer[WebPendingRequest]
    raisedHandsUserIdentities: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[int] = ..., room: _Optional[str] = ..., token: _Optional[str] = ..., url: _Optional[_Union[WebOffset, _Mapping]] = ..., video: _Optional[bool] = ..., createDate: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., duration: _Optional[_Union[WebInt32Value_1, _Mapping]] = ..., initiatorUserId: _Optional[int] = ..., peer: _Optional[_Union[WebOutPeer, _Mapping]] = ..., ext: _Optional[_Mapping[str, bytes]] = ..., mode: _Optional[int] = ..., link: _Optional[str] = ..., isPublic: _Optional[bool] = ..., extra: _Optional[_Mapping[str, bytes]] = ..., title: _Optional[str] = ..., inCallParticipants: _Optional[_Iterable[_Union[WebOutPeer, _Mapping]]] = ..., endDate: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., pendingRequests: _Optional[_Iterable[_Union[WebPendingRequest, _Mapping]]] = ..., raisedHandsUserIdentities: _Optional[_Iterable[str]] = ...) -> None: ...

class WebGroupCallEnded(_message.Message):
    __slots__ = ("groupCall",)
    GROUPCALL_FIELD_NUMBER: _ClassVar[int]
    groupCall: WebGroupCall
    def __init__(self, groupCall: _Optional[_Union[WebGroupCall, _Mapping]] = ...) -> None: ...

class WebGroupCallStarted(_message.Message):
    __slots__ = ("groupCall", "seq")
    GROUPCALL_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    groupCall: WebGroupCall
    seq: int
    def __init__(self, groupCall: _Optional[_Union[WebGroupCall, _Mapping]] = ..., seq: _Optional[int] = ...) -> None: ...

class WebGroupCanInviteMembersChanged(_message.Message):
    __slots__ = ("groupId", "canInviteMembers")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    CANINVITEMEMBERS_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    canInviteMembers: bool
    def __init__(self, groupId: _Optional[int] = ..., canInviteMembers: _Optional[bool] = ...) -> None: ...

class WebGroupCanSendMessagesChanged(_message.Message):
    __slots__ = ("groupId", "canSendMessages")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    CANSENDMESSAGES_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    canSendMessages: bool
    def __init__(self, groupId: _Optional[int] = ..., canSendMessages: _Optional[bool] = ...) -> None: ...

class WebGroupCanViewMembersChanged(_message.Message):
    __slots__ = ("groupId", "canViewMembers")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    CANVIEWMEMBERS_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    canViewMembers: bool
    def __init__(self, groupId: _Optional[int] = ..., canViewMembers: _Optional[bool] = ...) -> None: ...

class WebGroupDefaultPermissionsChanged(_message.Message):
    __slots__ = ("group", "permissions")
    GROUP_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    group: WebGroupPeer
    permissions: WebPermissions
    def __init__(self, group: _Optional[_Union[WebGroupPeer, _Mapping]] = ..., permissions: _Optional[_Union[WebPermissions, _Mapping]] = ...) -> None: ...

class WebGroupExInfoChanged(_message.Message):
    __slots__ = ("groupId", "exInfo")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    EXINFO_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    exInfo: WebExInfo
    def __init__(self, groupId: _Optional[int] = ..., exInfo: _Optional[_Union[WebExInfo, _Mapping]] = ...) -> None: ...

class WebGroupExtChanged(_message.Message):
    __slots__ = ("groupId", "ext")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    ext: WebExt
    def __init__(self, groupId: _Optional[int] = ..., ext: _Optional[_Union[WebExt, _Mapping]] = ...) -> None: ...

class WebGroupFullExtChanged(_message.Message):
    __slots__ = ("groupId", "ext")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    ext: WebExt
    def __init__(self, groupId: _Optional[int] = ..., ext: _Optional[_Union[WebExt, _Mapping]] = ...) -> None: ...

class WebGroupHistoryShared(_message.Message):
    __slots__ = ("groupId",)
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    def __init__(self, groupId: _Optional[int] = ...) -> None: ...

class WebGroupInviteObsolete(_message.Message):
    __slots__ = ("groupId", "inviteUid", "date", "rid", "seq", "isJoined")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    INVITEUID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    ISJOINED_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    inviteUid: int
    date: int
    rid: int
    seq: WebInt32Value
    isJoined: bool
    def __init__(self, groupId: _Optional[int] = ..., inviteUid: _Optional[int] = ..., date: _Optional[int] = ..., rid: _Optional[int] = ..., seq: _Optional[_Union[WebInt32Value, _Mapping]] = ..., isJoined: _Optional[bool] = ...) -> None: ...

class WebGroupMemberAdminChanged(_message.Message):
    __slots__ = ("groupId", "userId", "isAdmin")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    USERID_FIELD_NUMBER: _ClassVar[int]
    ISADMIN_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    userId: int
    isAdmin: bool
    def __init__(self, groupId: _Optional[int] = ..., userId: _Optional[int] = ..., isAdmin: _Optional[bool] = ...) -> None: ...

class WebGroupMemberChanged(_message.Message):
    __slots__ = ("groupId", "isMember")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    ISMEMBER_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    isMember: bool
    def __init__(self, groupId: _Optional[int] = ..., isMember: _Optional[bool] = ...) -> None: ...

class WebGroupMemberDiff(_message.Message):
    __slots__ = ("removedUsers", "addedMembers", "membersCount")
    REMOVEDUSERS_FIELD_NUMBER: _ClassVar[int]
    ADDEDMEMBERS_FIELD_NUMBER: _ClassVar[int]
    MEMBERSCOUNT_FIELD_NUMBER: _ClassVar[int]
    removedUsers: _containers.RepeatedScalarFieldContainer[int]
    addedMembers: _containers.RepeatedCompositeFieldContainer[WebMember]
    membersCount: int
    def __init__(self, removedUsers: _Optional[_Iterable[int]] = ..., addedMembers: _Optional[_Iterable[_Union[WebMember, _Mapping]]] = ..., membersCount: _Optional[int] = ...) -> None: ...

class WebGroupMemberPermissionsChanged(_message.Message):
    __slots__ = ("groupId", "uid", "permissions")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    uid: int
    permissions: WebPermissions
    def __init__(self, groupId: _Optional[int] = ..., uid: _Optional[int] = ..., permissions: _Optional[_Union[WebPermissions, _Mapping]] = ...) -> None: ...

class WebGroupMembersBecameAsync(_message.Message):
    __slots__ = ("groupId",)
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    def __init__(self, groupId: _Optional[int] = ...) -> None: ...

class WebGroupMembersCountChanged(_message.Message):
    __slots__ = ("groupId", "membersCount")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    MEMBERSCOUNT_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    membersCount: int
    def __init__(self, groupId: _Optional[int] = ..., membersCount: _Optional[int] = ...) -> None: ...

class WebGroupMembersUpdated(_message.Message):
    __slots__ = ("groupId", "members")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    members: _containers.RepeatedCompositeFieldContainer[WebMember]
    def __init__(self, groupId: _Optional[int] = ..., members: _Optional[_Iterable[_Union[WebMember, _Mapping]]] = ...) -> None: ...

class WebGroupMembersUpdateObsolete(_message.Message):
    __slots__ = ("groupId", "members")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    members: _containers.RepeatedCompositeFieldContainer[WebMember]
    def __init__(self, groupId: _Optional[int] = ..., members: _Optional[_Iterable[_Union[WebMember, _Mapping]]] = ...) -> None: ...

class WebGroupMessagePinned(_message.Message):
    __slots__ = ("groupId", "message")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    message: WebHistory
    def __init__(self, groupId: _Optional[int] = ..., message: _Optional[_Union[WebHistory, _Mapping]] = ...) -> None: ...

class WebGroupNicknameChanged(_message.Message):
    __slots__ = ("groupId", "uid", "nick", "date", "rid")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    NICK_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    uid: int
    nick: WebStringValue
    date: int
    rid: int
    def __init__(self, groupId: _Optional[int] = ..., uid: _Optional[int] = ..., nick: _Optional[_Union[WebStringValue, _Mapping]] = ..., date: _Optional[int] = ..., rid: _Optional[int] = ...) -> None: ...

class WebGroupOnline(_message.Message):
    __slots__ = ("groupId", "count")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    count: int
    def __init__(self, groupId: _Optional[int] = ..., count: _Optional[int] = ...) -> None: ...

class WebGroupOwnerChanged(_message.Message):
    __slots__ = ("groupId", "userId")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    USERID_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    userId: int
    def __init__(self, groupId: _Optional[int] = ..., userId: _Optional[int] = ...) -> None: ...

class WebGroupPeer(_message.Message):
    __slots__ = ("groupId", "accessHash")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    ACCESSHASH_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    accessHash: int
    def __init__(self, groupId: _Optional[int] = ..., accessHash: _Optional[int] = ...) -> None: ...

class WebGroupPinRemoved(_message.Message):
    __slots__ = ("groupId", "messageId")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    MESSAGEID_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    messageId: WebMessageId
    def __init__(self, groupId: _Optional[int] = ..., messageId: _Optional[_Union[WebMessageId, _Mapping]] = ...) -> None: ...

class WebGroupRestrictionChanged(_message.Message):
    __slots__ = ("groupId", "restriction")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    RESTRICTION_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    restriction: int
    def __init__(self, groupId: _Optional[int] = ..., restriction: _Optional[int] = ...) -> None: ...

class WebGroupTitleChanged(_message.Message):
    __slots__ = ("groupId", "title")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    title: str
    def __init__(self, groupId: _Optional[int] = ..., title: _Optional[str] = ...) -> None: ...

class WebGroupTitleChangedObsolete(_message.Message):
    __slots__ = ("groupId", "uid", "title", "date", "rid")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    uid: int
    title: str
    date: int
    rid: int
    def __init__(self, groupId: _Optional[int] = ..., uid: _Optional[int] = ..., title: _Optional[str] = ..., date: _Optional[int] = ..., rid: _Optional[int] = ...) -> None: ...

class WebGroupTopicChanged(_message.Message):
    __slots__ = ("groupId", "topic")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    TOPIC_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    topic: WebStringValue
    def __init__(self, groupId: _Optional[int] = ..., topic: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebGroupTopicChangedObsolete(_message.Message):
    __slots__ = ("groupId", "rid", "uid", "topic", "date")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    TOPIC_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    rid: int
    uid: int
    topic: WebStringValue
    date: int
    def __init__(self, groupId: _Optional[int] = ..., rid: _Optional[int] = ..., uid: _Optional[int] = ..., topic: _Optional[_Union[WebStringValue, _Mapping]] = ..., date: _Optional[int] = ...) -> None: ...

class WebGroupUserInvitedObsolete(_message.Message):
    __slots__ = ("groupId", "uid", "inviterUid", "date", "rid", "isJoined")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    INVITERUID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    ISJOINED_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    uid: int
    inviterUid: int
    date: int
    rid: int
    isJoined: bool
    def __init__(self, groupId: _Optional[int] = ..., uid: _Optional[int] = ..., inviterUid: _Optional[int] = ..., date: _Optional[int] = ..., rid: _Optional[int] = ..., isJoined: _Optional[bool] = ...) -> None: ...

class WebGroupUserKickObsolete(_message.Message):
    __slots__ = ("groupId", "uid", "kickerUid", "date", "rid")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    KICKERUID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    uid: int
    kickerUid: int
    date: int
    rid: int
    def __init__(self, groupId: _Optional[int] = ..., uid: _Optional[int] = ..., kickerUid: _Optional[int] = ..., date: _Optional[int] = ..., rid: _Optional[int] = ...) -> None: ...

class WebGroupUserLeaveObsolete(_message.Message):
    __slots__ = ("groupId", "uid", "date", "rid")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    groupId: int
    uid: int
    date: int
    rid: int
    def __init__(self, groupId: _Optional[int] = ..., uid: _Optional[int] = ..., date: _Optional[int] = ..., rid: _Optional[int] = ...) -> None: ...

class WebHidePrivacyBar(_message.Message):
    __slots__ = ("exPeer",)
    EXPEER_FIELD_NUMBER: _ClassVar[int]
    exPeer: WebExPeer
    def __init__(self, exPeer: _Optional[_Union[WebExPeer, _Mapping]] = ...) -> None: ...

class WebHistory(_message.Message):
    __slots__ = ("senderUid", "rid", "date", "message", "state", "reactions", "attribute", "quotedMessage", "seq", "previousMessageId", "nextMessageId", "editedAt", "editorUserId", "groupedId", "hasComment", "replies", "replyToTopId", "authorSign")
    SENDERUID_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    REACTIONS_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTE_FIELD_NUMBER: _ClassVar[int]
    QUOTEDMESSAGE_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    PREVIOUSMESSAGEID_FIELD_NUMBER: _ClassVar[int]
    NEXTMESSAGEID_FIELD_NUMBER: _ClassVar[int]
    EDITEDAT_FIELD_NUMBER: _ClassVar[int]
    EDITORUSERID_FIELD_NUMBER: _ClassVar[int]
    GROUPEDID_FIELD_NUMBER: _ClassVar[int]
    HASCOMMENT_FIELD_NUMBER: _ClassVar[int]
    REPLIES_FIELD_NUMBER: _ClassVar[int]
    REPLYTOTOPID_FIELD_NUMBER: _ClassVar[int]
    AUTHORSIGN_FIELD_NUMBER: _ClassVar[int]
    senderUid: int
    rid: int
    date: int
    message: WebMessage
    state: int
    reactions: _containers.RepeatedCompositeFieldContainer[WebReaction]
    attribute: WebAttributes
    quotedMessage: WebQuotedMessage
    seq: WebInt64Value_1
    previousMessageId: WebMessageId
    nextMessageId: WebMessageId
    editedAt: WebInt64Value_1
    editorUserId: WebInt32Value
    groupedId: WebInt64Value_1
    hasComment: WebBoolValue_1
    replies: WebRepliesInfo
    replyToTopId: WebMessageId
    authorSign: WebStringValue
    def __init__(self, senderUid: _Optional[int] = ..., rid: _Optional[int] = ..., date: _Optional[int] = ..., message: _Optional[_Union[WebMessage, _Mapping]] = ..., state: _Optional[int] = ..., reactions: _Optional[_Iterable[_Union[WebReaction, _Mapping]]] = ..., attribute: _Optional[_Union[WebAttributes, _Mapping]] = ..., quotedMessage: _Optional[_Union[WebQuotedMessage, _Mapping]] = ..., seq: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., previousMessageId: _Optional[_Union[WebMessageId, _Mapping]] = ..., nextMessageId: _Optional[_Union[WebMessageId, _Mapping]] = ..., editedAt: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., editorUserId: _Optional[_Union[WebInt32Value, _Mapping]] = ..., groupedId: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., hasComment: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., replies: _Optional[_Union[WebRepliesInfo, _Mapping]] = ..., replyToTopId: _Optional[_Union[WebMessageId, _Mapping]] = ..., authorSign: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebImageLocation(_message.Message):
    __slots__ = ("fileLocation", "width", "height", "fileSize")
    FILELOCATION_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FILESIZE_FIELD_NUMBER: _ClassVar[int]
    fileLocation: WebFileLocation
    width: int
    height: int
    fileSize: int
    def __init__(self, fileLocation: _Optional[_Union[WebFileLocation, _Mapping]] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., fileSize: _Optional[int] = ...) -> None: ...

class WebInfo(_message.Message):
    __slots__ = ("key", "groupId", "userCount", "isLive", "link", "hlsLink", "rtmpLink", "mainMessageId", "mainMessageDate")
    KEY_FIELD_NUMBER: _ClassVar[int]
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    USERCOUNT_FIELD_NUMBER: _ClassVar[int]
    ISLIVE_FIELD_NUMBER: _ClassVar[int]
    LINK_FIELD_NUMBER: _ClassVar[int]
    HLSLINK_FIELD_NUMBER: _ClassVar[int]
    RTMPLINK_FIELD_NUMBER: _ClassVar[int]
    MAINMESSAGEID_FIELD_NUMBER: _ClassVar[int]
    MAINMESSAGEDATE_FIELD_NUMBER: _ClassVar[int]
    key: int
    groupId: int
    userCount: int
    isLive: bool
    link: str
    hlsLink: str
    rtmpLink: str
    mainMessageId: int
    mainMessageDate: int
    def __init__(self, key: _Optional[int] = ..., groupId: _Optional[int] = ..., userCount: _Optional[int] = ..., isLive: _Optional[bool] = ..., link: _Optional[str] = ..., hlsLink: _Optional[str] = ..., rtmpLink: _Optional[str] = ..., mainMessageId: _Optional[int] = ..., mainMessageDate: _Optional[int] = ...) -> None: ...

class WebInlineKeyboardMarkup(_message.Message):
    __slots__ = ("listOfInlineList",)
    LISTOFINLINELIST_FIELD_NUMBER: _ClassVar[int]
    listOfInlineList: _containers.RepeatedCompositeFieldContainer[WebListOfInlineList]
    def __init__(self, listOfInlineList: _Optional[_Iterable[_Union[WebListOfInlineList, _Mapping]]] = ...) -> None: ...

class WebInlineList(_message.Message):
    __slots__ = ("text", "url", "callbackData", "webApp", "loginUrl", "switchInlineQuery", "switchInlineQueryCurrentChat", "switchInlineQueryChosenChat", "copyText", "authentication", "customAction", "sendData")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    CALLBACKDATA_FIELD_NUMBER: _ClassVar[int]
    WEBAPP_FIELD_NUMBER: _ClassVar[int]
    LOGINURL_FIELD_NUMBER: _ClassVar[int]
    SWITCHINLINEQUERY_FIELD_NUMBER: _ClassVar[int]
    SWITCHINLINEQUERYCURRENTCHAT_FIELD_NUMBER: _ClassVar[int]
    SWITCHINLINEQUERYCHOSENCHAT_FIELD_NUMBER: _ClassVar[int]
    COPYTEXT_FIELD_NUMBER: _ClassVar[int]
    AUTHENTICATION_FIELD_NUMBER: _ClassVar[int]
    CUSTOMACTION_FIELD_NUMBER: _ClassVar[int]
    SENDDATA_FIELD_NUMBER: _ClassVar[int]
    text: str
    url: WebStringValue
    callbackData: WebStringValue
    webApp: WebWebApp
    loginUrl: WebLoginUrl
    switchInlineQuery: WebStringValue
    switchInlineQueryCurrentChat: WebStringValue
    switchInlineQueryChosenChat: WebSwitchInlineQueryChosenChat
    copyText: WebCopyText
    authentication: WebAuthentication
    customAction: WebCustomAction
    sendData: WebBoolValue_1
    def __init__(self, text: _Optional[str] = ..., url: _Optional[_Union[WebStringValue, _Mapping]] = ..., callbackData: _Optional[_Union[WebStringValue, _Mapping]] = ..., webApp: _Optional[_Union[WebWebApp, _Mapping]] = ..., loginUrl: _Optional[_Union[WebLoginUrl, _Mapping]] = ..., switchInlineQuery: _Optional[_Union[WebStringValue, _Mapping]] = ..., switchInlineQueryCurrentChat: _Optional[_Union[WebStringValue, _Mapping]] = ..., switchInlineQueryChosenChat: _Optional[_Union[WebSwitchInlineQueryChosenChat, _Mapping]] = ..., copyText: _Optional[_Union[WebCopyText, _Mapping]] = ..., authentication: _Optional[_Union[WebAuthentication, _Mapping]] = ..., customAction: _Optional[_Union[WebCustomAction, _Mapping]] = ..., sendData: _Optional[_Union[WebBoolValue_1, _Mapping]] = ...) -> None: ...

class WebInt32Value(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class WebInt32Value_1(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class WebInt64Value_1(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class WebIntro(_message.Message):
    __slots__ = ("text", "fileLocation", "width", "height", "fileSize", "mimeType", "fileName", "thumb")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    FILELOCATION_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FILESIZE_FIELD_NUMBER: _ClassVar[int]
    MIMETYPE_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    THUMB_FIELD_NUMBER: _ClassVar[int]
    text: WebStringValue
    fileLocation: WebFileLocation
    width: int
    height: int
    fileSize: int
    mimeType: str
    fileName: str
    thumb: WebThumb
    def __init__(self, text: _Optional[_Union[WebStringValue, _Mapping]] = ..., fileLocation: _Optional[_Union[WebFileLocation, _Mapping]] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., fileSize: _Optional[int] = ..., mimeType: _Optional[str] = ..., fileName: _Optional[str] = ..., thumb: _Optional[_Union[WebThumb, _Mapping]] = ...) -> None: ...

class WebIntroGif(_message.Message):
    __slots__ = ("thumb", "width", "height")
    THUMB_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    thumb: WebThumb
    width: int
    height: int
    def __init__(self, thumb: _Optional[_Union[WebThumb, _Mapping]] = ..., width: _Optional[int] = ..., height: _Optional[int] = ...) -> None: ...

class WebIntroMessage(_message.Message):
    __slots__ = ("text", "media")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    MEDIA_FIELD_NUMBER: _ClassVar[int]
    text: WebStringValue
    media: WebT_w_59727
    def __init__(self, text: _Optional[_Union[WebStringValue, _Mapping]] = ..., media: _Optional[_Union[WebT_w_59727, _Mapping]] = ...) -> None: ...

class WebIntroPhoto(_message.Message):
    __slots__ = ("thumb", "width", "height")
    THUMB_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    thumb: WebThumb
    width: int
    height: int
    def __init__(self, thumb: _Optional[_Union[WebThumb, _Mapping]] = ..., width: _Optional[int] = ..., height: _Optional[int] = ...) -> None: ...

class WebJsonMessage(_message.Message):
    __slots__ = ("rawJson",)
    RAWJSON_FIELD_NUMBER: _ClassVar[int]
    rawJson: str
    def __init__(self, rawJson: _Optional[str] = ...) -> None: ...

class WebKeyboardList(_message.Message):
    __slots__ = ("text", "requestContact", "requestLocation", "requestUser", "requestChat", "requestPoll", "webApp", "customAction", "sendMessage")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    REQUESTCONTACT_FIELD_NUMBER: _ClassVar[int]
    REQUESTLOCATION_FIELD_NUMBER: _ClassVar[int]
    REQUESTUSER_FIELD_NUMBER: _ClassVar[int]
    REQUESTCHAT_FIELD_NUMBER: _ClassVar[int]
    REQUESTPOLL_FIELD_NUMBER: _ClassVar[int]
    WEBAPP_FIELD_NUMBER: _ClassVar[int]
    CUSTOMACTION_FIELD_NUMBER: _ClassVar[int]
    SENDMESSAGE_FIELD_NUMBER: _ClassVar[int]
    text: str
    requestContact: WebBoolValue_1
    requestLocation: WebBoolValue_1
    requestUser: WebRequestUser
    requestChat: WebRequestChat
    requestPoll: WebRequestPoll
    webApp: WebWebApp
    customAction: WebCustomAction
    sendMessage: WebBoolValue_1
    def __init__(self, text: _Optional[str] = ..., requestContact: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., requestLocation: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., requestUser: _Optional[_Union[WebRequestUser, _Mapping]] = ..., requestChat: _Optional[_Union[WebRequestChat, _Mapping]] = ..., requestPoll: _Optional[_Union[WebRequestPoll, _Mapping]] = ..., webApp: _Optional[_Union[WebWebApp, _Mapping]] = ..., customAction: _Optional[_Union[WebCustomAction, _Mapping]] = ..., sendMessage: _Optional[_Union[WebBoolValue_1, _Mapping]] = ...) -> None: ...

class WebLinkPreview(_message.Message):
    __slots__ = ("linkPreviewType", "openGraphObject")
    LINKPREVIEWTYPE_FIELD_NUMBER: _ClassVar[int]
    OPENGRAPHOBJECT_FIELD_NUMBER: _ClassVar[int]
    linkPreviewType: int
    openGraphObject: WebOpenGraphObject
    def __init__(self, linkPreviewType: _Optional[int] = ..., openGraphObject: _Optional[_Union[WebOpenGraphObject, _Mapping]] = ...) -> None: ...

class WebList(_message.Message):
    __slots__ = ("array",)
    ARRAY_FIELD_NUMBER: _ClassVar[int]
    array: _containers.RepeatedCompositeFieldContainer[WebValue]
    def __init__(self, array: _Optional[_Iterable[_Union[WebValue, _Mapping]]] = ...) -> None: ...

class WebListOfInlineList(_message.Message):
    __slots__ = ("inlineList",)
    INLINELIST_FIELD_NUMBER: _ClassVar[int]
    inlineList: _containers.RepeatedCompositeFieldContainer[WebInlineList]
    def __init__(self, inlineList: _Optional[_Iterable[_Union[WebInlineList, _Mapping]]] = ...) -> None: ...

class WebListOfKeyboardList(_message.Message):
    __slots__ = ("keyboardList",)
    KEYBOARDLIST_FIELD_NUMBER: _ClassVar[int]
    keyboardList: _containers.RepeatedCompositeFieldContainer[WebKeyboardList]
    def __init__(self, keyboardList: _Optional[_Iterable[_Union[WebKeyboardList, _Mapping]]] = ...) -> None: ...

class WebLiveMessage(_message.Message):
    __slots__ = ("link", "userCount", "isLive", "media", "key")
    LINK_FIELD_NUMBER: _ClassVar[int]
    USERCOUNT_FIELD_NUMBER: _ClassVar[int]
    ISLIVE_FIELD_NUMBER: _ClassVar[int]
    MEDIA_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    link: str
    userCount: int
    isLive: bool
    media: WebMedia
    key: int
    def __init__(self, link: _Optional[str] = ..., userCount: _Optional[int] = ..., isLive: _Optional[bool] = ..., media: _Optional[_Union[WebMedia, _Mapping]] = ..., key: _Optional[int] = ...) -> None: ...

class WebLoginUrl(_message.Message):
    __slots__ = ("url", "forwardText", "botUsername", "requestWriteAccess")
    URL_FIELD_NUMBER: _ClassVar[int]
    FORWARDTEXT_FIELD_NUMBER: _ClassVar[int]
    BOTUSERNAME_FIELD_NUMBER: _ClassVar[int]
    REQUESTWRITEACCESS_FIELD_NUMBER: _ClassVar[int]
    url: str
    forwardText: str
    botUsername: str
    requestWriteAccess: bool
    def __init__(self, url: _Optional[str] = ..., forwardText: _Optional[str] = ..., botUsername: _Optional[str] = ..., requestWriteAccess: _Optional[bool] = ...) -> None: ...

class WebLongTextMessage(_message.Message):
    __slots__ = ("text", "mentions", "extendedText", "extendedTextFileSize")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    MENTIONS_FIELD_NUMBER: _ClassVar[int]
    EXTENDEDTEXT_FIELD_NUMBER: _ClassVar[int]
    EXTENDEDTEXTFILESIZE_FIELD_NUMBER: _ClassVar[int]
    text: str
    mentions: _containers.RepeatedScalarFieldContainer[int]
    extendedText: WebFileLocation
    extendedTextFileSize: int
    def __init__(self, text: _Optional[str] = ..., mentions: _Optional[_Iterable[int]] = ..., extendedText: _Optional[_Union[WebFileLocation, _Mapping]] = ..., extendedTextFileSize: _Optional[int] = ...) -> None: ...

class WebLowerHand(_message.Message):
    __slots__ = ("userIdentity",)
    USERIDENTITY_FIELD_NUMBER: _ClassVar[int]
    userIdentity: str
    def __init__(self, userIdentity: _Optional[str] = ...) -> None: ...

class WebMedia(_message.Message):
    __slots__ = ("fileId", "accessHash", "fileSize", "name", "mimeType", "thumb", "ext", "caption", "checkSum", "algorithm", "fileStorageVersion", "groupedId", "messageTag")
    FILEID_FIELD_NUMBER: _ClassVar[int]
    ACCESSHASH_FIELD_NUMBER: _ClassVar[int]
    FILESIZE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MIMETYPE_FIELD_NUMBER: _ClassVar[int]
    THUMB_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    CAPTION_FIELD_NUMBER: _ClassVar[int]
    CHECKSUM_FIELD_NUMBER: _ClassVar[int]
    ALGORITHM_FIELD_NUMBER: _ClassVar[int]
    FILESTORAGEVERSION_FIELD_NUMBER: _ClassVar[int]
    GROUPEDID_FIELD_NUMBER: _ClassVar[int]
    MESSAGETAG_FIELD_NUMBER: _ClassVar[int]
    fileId: int
    accessHash: int
    fileSize: int
    name: str
    mimeType: str
    thumb: WebThumb
    ext: WebT_LnR
    caption: WebTextMessage
    checkSum: WebStringValue
    algorithm: WebStringValue
    fileStorageVersion: WebInt32Value
    groupedId: WebInt64Value_1
    messageTag: WebMessageTag
    def __init__(self, fileId: _Optional[int] = ..., accessHash: _Optional[int] = ..., fileSize: _Optional[int] = ..., name: _Optional[str] = ..., mimeType: _Optional[str] = ..., thumb: _Optional[_Union[WebThumb, _Mapping]] = ..., ext: _Optional[_Union[WebT_LnR, _Mapping]] = ..., caption: _Optional[_Union[WebTextMessage, _Mapping]] = ..., checkSum: _Optional[_Union[WebStringValue, _Mapping]] = ..., algorithm: _Optional[_Union[WebStringValue, _Mapping]] = ..., fileStorageVersion: _Optional[_Union[WebInt32Value, _Mapping]] = ..., groupedId: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., messageTag: _Optional[_Union[WebMessageTag, _Mapping]] = ...) -> None: ...

class WebMediaExtra(_message.Message):
    __slots__ = ("introGif", "introPhoto")
    INTROGIF_FIELD_NUMBER: _ClassVar[int]
    INTROPHOTO_FIELD_NUMBER: _ClassVar[int]
    introGif: WebIntroGif
    introPhoto: WebIntroPhoto
    def __init__(self, introGif: _Optional[_Union[WebIntroGif, _Mapping]] = ..., introPhoto: _Optional[_Union[WebIntroPhoto, _Mapping]] = ...) -> None: ...

class WebMember(_message.Message):
    __slots__ = ("uid", "inviterUid", "date", "isAdmin", "promoterUserId", "promotedAt", "permissions", "title")
    UID_FIELD_NUMBER: _ClassVar[int]
    INVITERUID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    ISADMIN_FIELD_NUMBER: _ClassVar[int]
    PROMOTERUSERID_FIELD_NUMBER: _ClassVar[int]
    PROMOTEDAT_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    uid: int
    inviterUid: int
    date: int
    isAdmin: WebBoolValue_1
    promoterUserId: WebInt32Value
    promotedAt: WebInt64Value_1
    permissions: WebPermissions
    title: WebStringValue
    def __init__(self, uid: _Optional[int] = ..., inviterUid: _Optional[int] = ..., date: _Optional[int] = ..., isAdmin: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., promoterUserId: _Optional[_Union[WebInt32Value, _Mapping]] = ..., promotedAt: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., permissions: _Optional[_Union[WebPermissions, _Mapping]] = ..., title: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebMentionReadByMe(_message.Message):
    __slots__ = ("peer", "messageId")
    PEER_FIELD_NUMBER: _ClassVar[int]
    MESSAGEID_FIELD_NUMBER: _ClassVar[int]
    peer: WebExPeer
    messageId: WebMessageId
    def __init__(self, peer: _Optional[_Union[WebExPeer, _Mapping]] = ..., messageId: _Optional[_Union[WebMessageId, _Mapping]] = ...) -> None: ...

class WebMessage(_message.Message):
    __slots__ = ("bankMessage", "binaryMessage", "deletedMessage", "documentMessage", "emptyMessage", "jsonMessage", "nasimEncryptedMessage", "orderMessage", "purchaseMessage", "serviceMessage", "stickerMessage", "templateMessage", "templateMessageResponse", "textMessage", "unsupportedMessage", "giftPacketMessage", "premiumMessage", "newPremiumMessage", "boughtPremiumMessage", "advertisementMessage", "crowdFundingMessage", "animatedStickerMessage", "bannedMessage", "liveMessage", "protectedMessage", "goldGiftPacketMessage", "pollMessage", "longTextMessage", "streamedMessage", "story")
    BANKMESSAGE_FIELD_NUMBER: _ClassVar[int]
    BINARYMESSAGE_FIELD_NUMBER: _ClassVar[int]
    DELETEDMESSAGE_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTMESSAGE_FIELD_NUMBER: _ClassVar[int]
    EMPTYMESSAGE_FIELD_NUMBER: _ClassVar[int]
    JSONMESSAGE_FIELD_NUMBER: _ClassVar[int]
    NASIMENCRYPTEDMESSAGE_FIELD_NUMBER: _ClassVar[int]
    ORDERMESSAGE_FIELD_NUMBER: _ClassVar[int]
    PURCHASEMESSAGE_FIELD_NUMBER: _ClassVar[int]
    SERVICEMESSAGE_FIELD_NUMBER: _ClassVar[int]
    STICKERMESSAGE_FIELD_NUMBER: _ClassVar[int]
    TEMPLATEMESSAGE_FIELD_NUMBER: _ClassVar[int]
    TEMPLATEMESSAGERESPONSE_FIELD_NUMBER: _ClassVar[int]
    TEXTMESSAGE_FIELD_NUMBER: _ClassVar[int]
    UNSUPPORTEDMESSAGE_FIELD_NUMBER: _ClassVar[int]
    GIFTPACKETMESSAGE_FIELD_NUMBER: _ClassVar[int]
    PREMIUMMESSAGE_FIELD_NUMBER: _ClassVar[int]
    NEWPREMIUMMESSAGE_FIELD_NUMBER: _ClassVar[int]
    BOUGHTPREMIUMMESSAGE_FIELD_NUMBER: _ClassVar[int]
    ADVERTISEMENTMESSAGE_FIELD_NUMBER: _ClassVar[int]
    CROWDFUNDINGMESSAGE_FIELD_NUMBER: _ClassVar[int]
    ANIMATEDSTICKERMESSAGE_FIELD_NUMBER: _ClassVar[int]
    BANNEDMESSAGE_FIELD_NUMBER: _ClassVar[int]
    LIVEMESSAGE_FIELD_NUMBER: _ClassVar[int]
    PROTECTEDMESSAGE_FIELD_NUMBER: _ClassVar[int]
    GOLDGIFTPACKETMESSAGE_FIELD_NUMBER: _ClassVar[int]
    POLLMESSAGE_FIELD_NUMBER: _ClassVar[int]
    LONGTEXTMESSAGE_FIELD_NUMBER: _ClassVar[int]
    STREAMEDMESSAGE_FIELD_NUMBER: _ClassVar[int]
    STORY_FIELD_NUMBER: _ClassVar[int]
    bankMessage: WebBankMessage
    binaryMessage: WebBinaryMessage
    deletedMessage: WebDeletedMessage
    documentMessage: WebMedia
    emptyMessage: WebEmptyMessage
    jsonMessage: WebJsonMessage
    nasimEncryptedMessage: WebNasimEncryptedMessage
    orderMessage: WebOrderMessage
    purchaseMessage: WebPurchaseMessage
    serviceMessage: WebServiceMessage
    stickerMessage: WebStickerMessage
    templateMessage: WebTemplateMessage
    templateMessageResponse: WebTemplateMessageResponse
    textMessage: WebTextMessage
    unsupportedMessage: WebUnsupportedMessage
    giftPacketMessage: WebGiftPacketMessage
    premiumMessage: WebPremiumMessage
    newPremiumMessage: WebNewPremiumMessage
    boughtPremiumMessage: WebBoughtPremiumMessage
    advertisementMessage: WebAdvertisementMessage
    crowdFundingMessage: WebCrowdFundingMessage
    animatedStickerMessage: WebAnimatedStickerMessage
    bannedMessage: WebBannedMessage
    liveMessage: WebLiveMessage
    protectedMessage: WebProtectedMessage
    goldGiftPacketMessage: WebGoldGiftPacketMessage
    pollMessage: WebPollMessage
    longTextMessage: WebLongTextMessage
    streamedMessage: WebStreamedMessage
    story: WebStoryType
    def __init__(self, bankMessage: _Optional[_Union[WebBankMessage, _Mapping]] = ..., binaryMessage: _Optional[_Union[WebBinaryMessage, _Mapping]] = ..., deletedMessage: _Optional[_Union[WebDeletedMessage, _Mapping]] = ..., documentMessage: _Optional[_Union[WebMedia, _Mapping]] = ..., emptyMessage: _Optional[_Union[WebEmptyMessage, _Mapping]] = ..., jsonMessage: _Optional[_Union[WebJsonMessage, _Mapping]] = ..., nasimEncryptedMessage: _Optional[_Union[WebNasimEncryptedMessage, _Mapping]] = ..., orderMessage: _Optional[_Union[WebOrderMessage, _Mapping]] = ..., purchaseMessage: _Optional[_Union[WebPurchaseMessage, _Mapping]] = ..., serviceMessage: _Optional[_Union[WebServiceMessage, _Mapping]] = ..., stickerMessage: _Optional[_Union[WebStickerMessage, _Mapping]] = ..., templateMessage: _Optional[_Union[WebTemplateMessage, _Mapping]] = ..., templateMessageResponse: _Optional[_Union[WebTemplateMessageResponse, _Mapping]] = ..., textMessage: _Optional[_Union[WebTextMessage, _Mapping]] = ..., unsupportedMessage: _Optional[_Union[WebUnsupportedMessage, _Mapping]] = ..., giftPacketMessage: _Optional[_Union[WebGiftPacketMessage, _Mapping]] = ..., premiumMessage: _Optional[_Union[WebPremiumMessage, _Mapping]] = ..., newPremiumMessage: _Optional[_Union[WebNewPremiumMessage, _Mapping]] = ..., boughtPremiumMessage: _Optional[_Union[WebBoughtPremiumMessage, _Mapping]] = ..., advertisementMessage: _Optional[_Union[WebAdvertisementMessage, _Mapping]] = ..., crowdFundingMessage: _Optional[_Union[WebCrowdFundingMessage, _Mapping]] = ..., animatedStickerMessage: _Optional[_Union[WebAnimatedStickerMessage, _Mapping]] = ..., bannedMessage: _Optional[_Union[WebBannedMessage, _Mapping]] = ..., liveMessage: _Optional[_Union[WebLiveMessage, _Mapping]] = ..., protectedMessage: _Optional[_Union[WebProtectedMessage, _Mapping]] = ..., goldGiftPacketMessage: _Optional[_Union[WebGoldGiftPacketMessage, _Mapping]] = ..., pollMessage: _Optional[_Union[WebPollMessage, _Mapping]] = ..., longTextMessage: _Optional[_Union[WebLongTextMessage, _Mapping]] = ..., streamedMessage: _Optional[_Union[WebStreamedMessage, _Mapping]] = ..., story: _Optional[_Union[WebStoryType, _Mapping]] = ...) -> None: ...

class WebMessageDateChanged(_message.Message):
    __slots__ = ("peer", "rid", "date")
    PEER_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    rid: int
    date: int
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., rid: _Optional[int] = ..., date: _Optional[int] = ...) -> None: ...

class WebMessageId(_message.Message):
    __slots__ = ("date", "rid", "seq")
    DATE_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    date: int
    rid: int
    seq: int
    def __init__(self, date: _Optional[int] = ..., rid: _Optional[int] = ..., seq: _Optional[int] = ...) -> None: ...

class WebMessageNewReaction(_message.Message):
    __slots__ = ("exPeer", "messageId")
    EXPEER_FIELD_NUMBER: _ClassVar[int]
    MESSAGEID_FIELD_NUMBER: _ClassVar[int]
    exPeer: WebExPeer
    messageId: WebMessageId
    def __init__(self, exPeer: _Optional[_Union[WebExPeer, _Mapping]] = ..., messageId: _Optional[_Union[WebMessageId, _Mapping]] = ...) -> None: ...

class WebMessagePinned(_message.Message):
    __slots__ = ("peer", "pinnedMessage")
    PEER_FIELD_NUMBER: _ClassVar[int]
    PINNEDMESSAGE_FIELD_NUMBER: _ClassVar[int]
    peer: WebExPeer
    pinnedMessage: WebHistory
    def __init__(self, peer: _Optional[_Union[WebExPeer, _Mapping]] = ..., pinnedMessage: _Optional[_Union[WebHistory, _Mapping]] = ...) -> None: ...

class WebMessageQuotedChanged(_message.Message):
    __slots__ = ("peer", "rid", "quotedMessage")
    PEER_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    QUOTEDMESSAGE_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    rid: int
    quotedMessage: WebQuotedMessage
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., rid: _Optional[int] = ..., quotedMessage: _Optional[_Union[WebQuotedMessage, _Mapping]] = ...) -> None: ...

class WebMessageReaction(_message.Message):
    __slots__ = ("peer", "rid", "reactions", "date")
    PEER_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    REACTIONS_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    rid: int
    reactions: _containers.RepeatedCompositeFieldContainer[WebReaction]
    date: int
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., rid: _Optional[int] = ..., reactions: _Optional[_Iterable[_Union[WebReaction, _Mapping]]] = ..., date: _Optional[int] = ...) -> None: ...

class WebMessageReactionsReadByMe(_message.Message):
    __slots__ = ("exPeer", "messageId")
    EXPEER_FIELD_NUMBER: _ClassVar[int]
    MESSAGEID_FIELD_NUMBER: _ClassVar[int]
    exPeer: WebExPeer
    messageId: WebMessageId
    def __init__(self, exPeer: _Optional[_Union[WebExPeer, _Mapping]] = ..., messageId: _Optional[_Union[WebMessageId, _Mapping]] = ...) -> None: ...

class WebMessageRead(_message.Message):
    __slots__ = ("peer", "startDate", "readDate")
    PEER_FIELD_NUMBER: _ClassVar[int]
    STARTDATE_FIELD_NUMBER: _ClassVar[int]
    READDATE_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    startDate: int
    readDate: int
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., startDate: _Optional[int] = ..., readDate: _Optional[int] = ...) -> None: ...

class WebMessageReadByMe(_message.Message):
    __slots__ = ("peer", "startDate", "unreadCounter", "endDate")
    PEER_FIELD_NUMBER: _ClassVar[int]
    STARTDATE_FIELD_NUMBER: _ClassVar[int]
    UNREADCOUNTER_FIELD_NUMBER: _ClassVar[int]
    ENDDATE_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    startDate: int
    unreadCounter: WebInt32Value
    endDate: WebInt64Value_1
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., startDate: _Optional[int] = ..., unreadCounter: _Optional[_Union[WebInt32Value, _Mapping]] = ..., endDate: _Optional[_Union[WebInt64Value_1, _Mapping]] = ...) -> None: ...

class WebMessageReceived(_message.Message):
    __slots__ = ("peer", "startDate", "receivedDate")
    PEER_FIELD_NUMBER: _ClassVar[int]
    STARTDATE_FIELD_NUMBER: _ClassVar[int]
    RECEIVEDDATE_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    startDate: int
    receivedDate: int
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., startDate: _Optional[int] = ..., receivedDate: _Optional[int] = ...) -> None: ...

class WebMessages(_message.Message):
    __slots__ = ("peer", "messageContainers")
    PEER_FIELD_NUMBER: _ClassVar[int]
    MESSAGECONTAINERS_FIELD_NUMBER: _ClassVar[int]
    peer: WebExPeer
    messageContainers: _containers.RepeatedCompositeFieldContainer[WebHistory]
    def __init__(self, peer: _Optional[_Union[WebExPeer, _Mapping]] = ..., messageContainers: _Optional[_Iterable[_Union[WebHistory, _Mapping]]] = ...) -> None: ...

class WebMessageSent(_message.Message):
    __slots__ = ("peer", "rid", "date", "previousMessageId")
    PEER_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    PREVIOUSMESSAGEID_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    rid: int
    date: int
    previousMessageId: WebMessageId
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., rid: _Optional[int] = ..., date: _Optional[int] = ..., previousMessageId: _Optional[_Union[WebMessageId, _Mapping]] = ...) -> None: ...

class WebMessageStreamChunks(_message.Message):
    __slots__ = ("exPeer", "messageId", "chunks")
    EXPEER_FIELD_NUMBER: _ClassVar[int]
    MESSAGEID_FIELD_NUMBER: _ClassVar[int]
    CHUNKS_FIELD_NUMBER: _ClassVar[int]
    exPeer: WebExPeer
    messageId: WebMessageId
    chunks: _containers.RepeatedCompositeFieldContainer[WebChunk]
    def __init__(self, exPeer: _Optional[_Union[WebExPeer, _Mapping]] = ..., messageId: _Optional[_Union[WebMessageId, _Mapping]] = ..., chunks: _Optional[_Iterable[_Union[WebChunk, _Mapping]]] = ...) -> None: ...

class WebMessagesUnPinned(_message.Message):
    __slots__ = ("messageIds", "peer", "all")
    MESSAGEIDS_FIELD_NUMBER: _ClassVar[int]
    PEER_FIELD_NUMBER: _ClassVar[int]
    ALL_FIELD_NUMBER: _ClassVar[int]
    messageIds: _containers.RepeatedCompositeFieldContainer[WebMessageId]
    peer: WebExPeer
    all: bool
    def __init__(self, messageIds: _Optional[_Iterable[_Union[WebMessageId, _Mapping]]] = ..., peer: _Optional[_Union[WebExPeer, _Mapping]] = ..., all: _Optional[bool] = ...) -> None: ...

class WebMessageTag(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class WebMultiMedia(_message.Message):
    __slots__ = ("randomId", "media")
    RANDOMID_FIELD_NUMBER: _ClassVar[int]
    MEDIA_FIELD_NUMBER: _ClassVar[int]
    randomId: int
    media: WebMedia
    def __init__(self, randomId: _Optional[int] = ..., media: _Optional[_Union[WebMedia, _Mapping]] = ...) -> None: ...

class WebMultiPeerCallStarted(_message.Message):
    __slots__ = ("id", "room", "url", "initiator", "peer", "mode", "extra", "callCreateDate", "updateCreateDate", "participants")
    class ExtraEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    ROOM_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    INITIATOR_FIELD_NUMBER: _ClassVar[int]
    PEER_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    CALLCREATEDATE_FIELD_NUMBER: _ClassVar[int]
    UPDATECREATEDATE_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    id: int
    room: str
    url: str
    initiator: int
    peer: WebOutPeer
    mode: int
    extra: _containers.ScalarMap[str, bytes]
    callCreateDate: int
    updateCreateDate: int
    participants: _containers.RepeatedCompositeFieldContainer[WebOutPeer]
    def __init__(self, id: _Optional[int] = ..., room: _Optional[str] = ..., url: _Optional[str] = ..., initiator: _Optional[int] = ..., peer: _Optional[_Union[WebOutPeer, _Mapping]] = ..., mode: _Optional[int] = ..., extra: _Optional[_Mapping[str, bytes]] = ..., callCreateDate: _Optional[int] = ..., updateCreateDate: _Optional[int] = ..., participants: _Optional[_Iterable[_Union[WebOutPeer, _Mapping]]] = ...) -> None: ...

class WebMultiplexingData(_message.Message):
    __slots__ = ("multiplexingType", "multiplexingRows")
    MULTIPLEXINGTYPE_FIELD_NUMBER: _ClassVar[int]
    MULTIPLEXINGROWS_FIELD_NUMBER: _ClassVar[int]
    multiplexingType: int
    multiplexingRows: _containers.RepeatedCompositeFieldContainer[WebMultiplexingRow]
    def __init__(self, multiplexingType: _Optional[int] = ..., multiplexingRows: _Optional[_Iterable[_Union[WebMultiplexingRow, _Mapping]]] = ...) -> None: ...

class WebMultiplexingRow(_message.Message):
    __slots__ = ("ibanNumber", "value")
    IBANNUMBER_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    ibanNumber: int
    value: int
    def __init__(self, ibanNumber: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...

class WebNasimEncryptedMessage(_message.Message):
    __slots__ = ("key", "message", "messageLength", "signature")
    KEY_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    MESSAGELENGTH_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    key: bytes
    message: bytes
    messageLength: int
    signature: bytes
    def __init__(self, key: _Optional[bytes] = ..., message: _Optional[bytes] = ..., messageLength: _Optional[int] = ..., signature: _Optional[bytes] = ...) -> None: ...

class WebNewPremiumMessage(_message.Message):
    __slots__ = ("amount", "targetWalletId", "originalMessage", "preview", "minimumRequiredDrmLevel")
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    TARGETWALLETID_FIELD_NUMBER: _ClassVar[int]
    ORIGINALMESSAGE_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_FIELD_NUMBER: _ClassVar[int]
    MINIMUMREQUIREDDRMLEVEL_FIELD_NUMBER: _ClassVar[int]
    amount: int
    targetWalletId: str
    originalMessage: WebMessage
    preview: WebMessage
    minimumRequiredDrmLevel: int
    def __init__(self, amount: _Optional[int] = ..., targetWalletId: _Optional[str] = ..., originalMessage: _Optional[_Union[WebMessage, _Mapping]] = ..., preview: _Optional[_Union[WebMessage, _Mapping]] = ..., minimumRequiredDrmLevel: _Optional[int] = ...) -> None: ...

class WebNewUpdate(_message.Message):
    __slots__ = ("update", "date")
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    update: WebUpdate
    date: int
    def __init__(self, update: _Optional[_Union[WebUpdate, _Mapping]] = ..., date: _Optional[int] = ...) -> None: ...

class WebOffset(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class WebOpenGraphObject(_message.Message):
    __slots__ = ("type", "url", "title", "description", "images")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IMAGES_FIELD_NUMBER: _ClassVar[int]
    type: str
    url: str
    title: str
    description: str
    images: _containers.RepeatedCompositeFieldContainer[WebT_E_95053]
    def __init__(self, type: _Optional[str] = ..., url: _Optional[str] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., images: _Optional[_Iterable[_Union[WebT_E_95053, _Mapping]]] = ...) -> None: ...

class WebOpenUrlAction(_message.Message):
    __slots__ = ("url", "browserType")
    URL_FIELD_NUMBER: _ClassVar[int]
    BROWSERTYPE_FIELD_NUMBER: _ClassVar[int]
    url: str
    browserType: int
    def __init__(self, url: _Optional[str] = ..., browserType: _Optional[int] = ...) -> None: ...

class WebOption(_message.Message):
    __slots__ = ("id", "text")
    ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    id: int
    text: str
    def __init__(self, id: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...

class WebOptionResult(_message.Message):
    __slots__ = ("optionId", "votesCount")
    OPTIONID_FIELD_NUMBER: _ClassVar[int]
    VOTESCOUNT_FIELD_NUMBER: _ClassVar[int]
    optionId: int
    votesCount: int
    def __init__(self, optionId: _Optional[int] = ..., votesCount: _Optional[int] = ...) -> None: ...

class WebOrderExt(_message.Message):
    __slots__ = ("billOrderMessage", "chargeOrderMessage", "psProxyOrderMessage")
    BILLORDERMESSAGE_FIELD_NUMBER: _ClassVar[int]
    CHARGEORDERMESSAGE_FIELD_NUMBER: _ClassVar[int]
    PSPROXYORDERMESSAGE_FIELD_NUMBER: _ClassVar[int]
    billOrderMessage: WebBillOrderMessage
    chargeOrderMessage: WebChargeOrderMessage
    psProxyOrderMessage: WebPsProxyOrderMessage
    def __init__(self, billOrderMessage: _Optional[_Union[WebBillOrderMessage, _Mapping]] = ..., chargeOrderMessage: _Optional[_Union[WebChargeOrderMessage, _Mapping]] = ..., psProxyOrderMessage: _Optional[_Union[WebPsProxyOrderMessage, _Mapping]] = ...) -> None: ...

class WebOrderMessage(_message.Message):
    __slots__ = ("orderExt",)
    ORDEREXT_FIELD_NUMBER: _ClassVar[int]
    orderExt: WebOrderExt
    def __init__(self, orderExt: _Optional[_Union[WebOrderExt, _Mapping]] = ...) -> None: ...

class WebOriginAccount(_message.Message):
    __slots__ = ("accountNumber", "branchCode", "openDate", "rate", "availableBalance", "lastMoneyTransferDate", "firstName", "lastName")
    ACCOUNTNUMBER_FIELD_NUMBER: _ClassVar[int]
    BRANCHCODE_FIELD_NUMBER: _ClassVar[int]
    OPENDATE_FIELD_NUMBER: _ClassVar[int]
    RATE_FIELD_NUMBER: _ClassVar[int]
    AVAILABLEBALANCE_FIELD_NUMBER: _ClassVar[int]
    LASTMONEYTRANSFERDATE_FIELD_NUMBER: _ClassVar[int]
    FIRSTNAME_FIELD_NUMBER: _ClassVar[int]
    LASTNAME_FIELD_NUMBER: _ClassVar[int]
    accountNumber: str
    branchCode: int
    openDate: int
    rate: int
    availableBalance: int
    lastMoneyTransferDate: int
    firstName: str
    lastName: str
    def __init__(self, accountNumber: _Optional[str] = ..., branchCode: _Optional[int] = ..., openDate: _Optional[int] = ..., rate: _Optional[int] = ..., availableBalance: _Optional[int] = ..., lastMoneyTransferDate: _Optional[int] = ..., firstName: _Optional[str] = ..., lastName: _Optional[str] = ...) -> None: ...

class WebOutPeer(_message.Message):
    __slots__ = ("type", "id", "accessHash")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    ACCESSHASH_FIELD_NUMBER: _ClassVar[int]
    type: int
    id: int
    accessHash: int
    def __init__(self, type: _Optional[int] = ..., id: _Optional[int] = ..., accessHash: _Optional[int] = ...) -> None: ...

class WebOwnStickersChanged(_message.Message):
    __slots__ = ("collections",)
    COLLECTIONS_FIELD_NUMBER: _ClassVar[int]
    collections: _containers.RepeatedCompositeFieldContainer[WebCollection]
    def __init__(self, collections: _Optional[_Iterable[_Union[WebCollection, _Mapping]]] = ...) -> None: ...

class WebParagraphColor(_message.Message):
    __slots__ = ("rgbColor", "predefinedColor")
    RGBCOLOR_FIELD_NUMBER: _ClassVar[int]
    PREDEFINEDCOLOR_FIELD_NUMBER: _ClassVar[int]
    rgbColor: WebRgbColor
    predefinedColor: WebPredefinedColor
    def __init__(self, rgbColor: _Optional[_Union[WebRgbColor, _Mapping]] = ..., predefinedColor: _Optional[_Union[WebPredefinedColor, _Mapping]] = ...) -> None: ...

class WebParameterChanged(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: WebStringValue
    def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebPeer(_message.Message):
    __slots__ = ("type", "id", "accessHash")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    ACCESSHASH_FIELD_NUMBER: _ClassVar[int]
    type: int
    id: int
    accessHash: int
    def __init__(self, type: _Optional[int] = ..., id: _Optional[int] = ..., accessHash: _Optional[int] = ...) -> None: ...

class WebPeerHaveScheduleTask(_message.Message):
    __slots__ = ("exPeer",)
    EXPEER_FIELD_NUMBER: _ClassVar[int]
    exPeer: WebExPeer
    def __init__(self, exPeer: _Optional[_Union[WebExPeer, _Mapping]] = ...) -> None: ...

class WebPeersInvited(_message.Message):
    __slots__ = ("callId", "invitees", "updateCreateDate")
    CALLID_FIELD_NUMBER: _ClassVar[int]
    INVITEES_FIELD_NUMBER: _ClassVar[int]
    UPDATECREATEDATE_FIELD_NUMBER: _ClassVar[int]
    callId: int
    invitees: _containers.RepeatedCompositeFieldContainer[WebOutPeer]
    updateCreateDate: int
    def __init__(self, callId: _Optional[int] = ..., invitees: _Optional[_Iterable[_Union[WebOutPeer, _Mapping]]] = ..., updateCreateDate: _Optional[int] = ...) -> None: ...

class WebPeersStateChanged(_message.Message):
    __slots__ = ("callId", "peerStates")
    CALLID_FIELD_NUMBER: _ClassVar[int]
    PEERSTATES_FIELD_NUMBER: _ClassVar[int]
    callId: int
    peerStates: _containers.RepeatedCompositeFieldContainer[WebPeerState]
    def __init__(self, callId: _Optional[int] = ..., peerStates: _Optional[_Iterable[_Union[WebPeerState, _Mapping]]] = ...) -> None: ...

class WebPeerState(_message.Message):
    __slots__ = ("id", "date", "peerStateEnum", "extra")
    class ExtraEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    PEERSTATEENUM_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    id: int
    date: int
    peerStateEnum: int
    extra: _containers.ScalarMap[str, bytes]
    def __init__(self, id: _Optional[int] = ..., date: _Optional[int] = ..., peerStateEnum: _Optional[int] = ..., extra: _Optional[_Mapping[str, bytes]] = ...) -> None: ...

class WebPendingRequest(_message.Message):
    __slots__ = ("requesterIdentifier", "name")
    REQUESTERIDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    requesterIdentifier: str
    name: str
    def __init__(self, requesterIdentifier: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class WebPermissions(_message.Message):
    __slots__ = ("seeMessage", "deleteMessage", "kickUser", "pinMessage", "inviteUser", "addAdmin", "changeInfo", "sendMessage", "seeMembers", "editMessage", "sendMedia", "sendGifStickers", "replyToStory", "forwardMessageFrom", "sendGiftPacket", "startCall", "sendLinkMessage", "sendForwardedMessage", "addStory", "manageCall")
    SEEMESSAGE_FIELD_NUMBER: _ClassVar[int]
    DELETEMESSAGE_FIELD_NUMBER: _ClassVar[int]
    KICKUSER_FIELD_NUMBER: _ClassVar[int]
    PINMESSAGE_FIELD_NUMBER: _ClassVar[int]
    INVITEUSER_FIELD_NUMBER: _ClassVar[int]
    ADDADMIN_FIELD_NUMBER: _ClassVar[int]
    CHANGEINFO_FIELD_NUMBER: _ClassVar[int]
    SENDMESSAGE_FIELD_NUMBER: _ClassVar[int]
    SEEMEMBERS_FIELD_NUMBER: _ClassVar[int]
    EDITMESSAGE_FIELD_NUMBER: _ClassVar[int]
    SENDMEDIA_FIELD_NUMBER: _ClassVar[int]
    SENDGIFSTICKERS_FIELD_NUMBER: _ClassVar[int]
    REPLYTOSTORY_FIELD_NUMBER: _ClassVar[int]
    FORWARDMESSAGEFROM_FIELD_NUMBER: _ClassVar[int]
    SENDGIFTPACKET_FIELD_NUMBER: _ClassVar[int]
    STARTCALL_FIELD_NUMBER: _ClassVar[int]
    SENDLINKMESSAGE_FIELD_NUMBER: _ClassVar[int]
    SENDFORWARDEDMESSAGE_FIELD_NUMBER: _ClassVar[int]
    ADDSTORY_FIELD_NUMBER: _ClassVar[int]
    MANAGECALL_FIELD_NUMBER: _ClassVar[int]
    seeMessage: bool
    deleteMessage: bool
    kickUser: bool
    pinMessage: bool
    inviteUser: bool
    addAdmin: bool
    changeInfo: bool
    sendMessage: bool
    seeMembers: bool
    editMessage: bool
    sendMedia: WebBoolValue_1
    sendGifStickers: WebBoolValue_1
    replyToStory: WebBoolValue_1
    forwardMessageFrom: WebBoolValue_1
    sendGiftPacket: WebBoolValue_1
    startCall: WebBoolValue_1
    sendLinkMessage: WebBoolValue_1
    sendForwardedMessage: WebBoolValue_1
    addStory: WebBoolValue_1
    manageCall: WebBoolValue_1
    def __init__(self, seeMessage: _Optional[bool] = ..., deleteMessage: _Optional[bool] = ..., kickUser: _Optional[bool] = ..., pinMessage: _Optional[bool] = ..., inviteUser: _Optional[bool] = ..., addAdmin: _Optional[bool] = ..., changeInfo: _Optional[bool] = ..., sendMessage: _Optional[bool] = ..., seeMembers: _Optional[bool] = ..., editMessage: _Optional[bool] = ..., sendMedia: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., sendGifStickers: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., replyToStory: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., forwardMessageFrom: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., sendGiftPacket: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., startCall: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., sendLinkMessage: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., sendForwardedMessage: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., addStory: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., manageCall: _Optional[_Union[WebBoolValue_1, _Mapping]] = ...) -> None: ...

class WebPhoneNumberChanged(_message.Message):
    __slots__ = ("userId", "phoneNumber")
    USERID_FIELD_NUMBER: _ClassVar[int]
    PHONENUMBER_FIELD_NUMBER: _ClassVar[int]
    userId: int
    phoneNumber: int
    def __init__(self, userId: _Optional[int] = ..., phoneNumber: _Optional[int] = ...) -> None: ...

class WebPinnedDialogsChanged(_message.Message):
    __slots__ = ("folderId", "pinnedDialogs", "pinnedPeers")
    FOLDERID_FIELD_NUMBER: _ClassVar[int]
    PINNEDDIALOGS_FIELD_NUMBER: _ClassVar[int]
    PINNEDPEERS_FIELD_NUMBER: _ClassVar[int]
    folderId: int
    pinnedDialogs: _containers.RepeatedCompositeFieldContainer[WebDialog]
    pinnedPeers: _containers.RepeatedCompositeFieldContainer[WebExPeer]
    def __init__(self, folderId: _Optional[int] = ..., pinnedDialogs: _Optional[_Iterable[_Union[WebDialog, _Mapping]]] = ..., pinnedPeers: _Optional[_Iterable[_Union[WebExPeer, _Mapping]]] = ...) -> None: ...

class WebPollMessage(_message.Message):
    __slots__ = ("question", "options", "isAnonymous", "type", "result", "pollId")
    QUESTION_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    ISANONYMOUS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    POLLID_FIELD_NUMBER: _ClassVar[int]
    question: str
    options: _containers.RepeatedCompositeFieldContainer[WebOption]
    isAnonymous: bool
    type: int
    result: WebPollResult
    pollId: int
    def __init__(self, question: _Optional[str] = ..., options: _Optional[_Iterable[_Union[WebOption, _Mapping]]] = ..., isAnonymous: _Optional[bool] = ..., type: _Optional[int] = ..., result: _Optional[_Union[WebPollResult, _Mapping]] = ..., pollId: _Optional[int] = ...) -> None: ...

class WebPollResult(_message.Message):
    __slots__ = ("optionResults", "recentVoters", "chosenOptionIds", "isClosed", "pollId", "votersCount")
    OPTIONRESULTS_FIELD_NUMBER: _ClassVar[int]
    RECENTVOTERS_FIELD_NUMBER: _ClassVar[int]
    CHOSENOPTIONIDS_FIELD_NUMBER: _ClassVar[int]
    ISCLOSED_FIELD_NUMBER: _ClassVar[int]
    POLLID_FIELD_NUMBER: _ClassVar[int]
    VOTERSCOUNT_FIELD_NUMBER: _ClassVar[int]
    optionResults: _containers.RepeatedCompositeFieldContainer[WebOptionResult]
    recentVoters: _containers.RepeatedScalarFieldContainer[int]
    chosenOptionIds: _containers.RepeatedScalarFieldContainer[int]
    isClosed: bool
    pollId: int
    votersCount: int
    def __init__(self, optionResults: _Optional[_Iterable[_Union[WebOptionResult, _Mapping]]] = ..., recentVoters: _Optional[_Iterable[int]] = ..., chosenOptionIds: _Optional[_Iterable[int]] = ..., isClosed: _Optional[bool] = ..., pollId: _Optional[int] = ..., votersCount: _Optional[int] = ...) -> None: ...

class WebPredefinedColor(_message.Message):
    __slots__ = ("color",)
    COLOR_FIELD_NUMBER: _ClassVar[int]
    color: int
    def __init__(self, color: _Optional[int] = ...) -> None: ...

class WebPremiumMessage(_message.Message):
    __slots__ = ("amount", "targetWalletId", "originalMessage", "preview", "fileMimeType")
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    TARGETWALLETID_FIELD_NUMBER: _ClassVar[int]
    ORIGINALMESSAGE_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_FIELD_NUMBER: _ClassVar[int]
    FILEMIMETYPE_FIELD_NUMBER: _ClassVar[int]
    amount: int
    targetWalletId: str
    originalMessage: WebMessage
    preview: WebMessage
    fileMimeType: WebStringValue
    def __init__(self, amount: _Optional[int] = ..., targetWalletId: _Optional[str] = ..., originalMessage: _Optional[_Union[WebMessage, _Mapping]] = ..., preview: _Optional[_Union[WebMessage, _Mapping]] = ..., fileMimeType: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebPremiumPurchaseStatus(_message.Message):
    __slots__ = ("successful", "failed", "unknown")
    SUCCESSFUL_FIELD_NUMBER: _ClassVar[int]
    FAILED_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FIELD_NUMBER: _ClassVar[int]
    successful: WebBoolValue_1
    failed: WebBoolValue_1
    unknown: WebBoolValue_1
    def __init__(self, successful: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., failed: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., unknown: _Optional[_Union[WebBoolValue_1, _Mapping]] = ...) -> None: ...

class WebProtectedMessage(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: WebMessage
    def __init__(self, message: _Optional[_Union[WebMessage, _Mapping]] = ...) -> None: ...

class WebPsProxyOrderMessage(_message.Message):
    __slots__ = ("psp", "productType", "productVersion", "parameters")
    PSP_FIELD_NUMBER: _ClassVar[int]
    PRODUCTTYPE_FIELD_NUMBER: _ClassVar[int]
    PRODUCTVERSION_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    psp: str
    productType: str
    productVersion: int
    parameters: WebExt
    def __init__(self, psp: _Optional[str] = ..., productType: _Optional[str] = ..., productVersion: _Optional[int] = ..., parameters: _Optional[_Union[WebExt, _Mapping]] = ...) -> None: ...

class WebPurchaseMessage(_message.Message):
    __slots__ = ("msg", "accountNumber", "amount", "regexAmount", "requestType", "multiplexingData", "additionalInfo", "targetWalletId")
    MSG_FIELD_NUMBER: _ClassVar[int]
    ACCOUNTNUMBER_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    REGEXAMOUNT_FIELD_NUMBER: _ClassVar[int]
    REQUESTTYPE_FIELD_NUMBER: _ClassVar[int]
    MULTIPLEXINGDATA_FIELD_NUMBER: _ClassVar[int]
    ADDITIONALINFO_FIELD_NUMBER: _ClassVar[int]
    TARGETWALLETID_FIELD_NUMBER: _ClassVar[int]
    msg: WebMessage
    accountNumber: str
    amount: int
    regexAmount: WebStringValue
    requestType: int
    multiplexingData: WebMultiplexingData
    additionalInfo: WebExt
    targetWalletId: WebStringValue
    def __init__(self, msg: _Optional[_Union[WebMessage, _Mapping]] = ..., accountNumber: _Optional[str] = ..., amount: _Optional[int] = ..., regexAmount: _Optional[_Union[WebStringValue, _Mapping]] = ..., requestType: _Optional[int] = ..., multiplexingData: _Optional[_Union[WebMultiplexingData, _Mapping]] = ..., additionalInfo: _Optional[_Union[WebExt, _Mapping]] = ..., targetWalletId: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebQuery(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: bytes
    def __init__(self, query: _Optional[bytes] = ...) -> None: ...

class WebQuotedMessage(_message.Message):
    __slots__ = ("messageId", "publicGroupId", "senderUserId", "messageDate", "quotedMessageContent", "quotedPeer", "story")
    MESSAGEID_FIELD_NUMBER: _ClassVar[int]
    PUBLICGROUPID_FIELD_NUMBER: _ClassVar[int]
    SENDERUSERID_FIELD_NUMBER: _ClassVar[int]
    MESSAGEDATE_FIELD_NUMBER: _ClassVar[int]
    QUOTEDMESSAGECONTENT_FIELD_NUMBER: _ClassVar[int]
    QUOTEDPEER_FIELD_NUMBER: _ClassVar[int]
    STORY_FIELD_NUMBER: _ClassVar[int]
    messageId: WebInt64Value_1
    publicGroupId: WebInt32Value
    senderUserId: int
    messageDate: int
    quotedMessageContent: WebMessage
    quotedPeer: WebPeer
    story: WebStoryType
    def __init__(self, messageId: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., publicGroupId: _Optional[_Union[WebInt32Value, _Mapping]] = ..., senderUserId: _Optional[int] = ..., messageDate: _Optional[int] = ..., quotedMessageContent: _Optional[_Union[WebMessage, _Mapping]] = ..., quotedPeer: _Optional[_Union[WebPeer, _Mapping]] = ..., story: _Optional[_Union[WebStoryType, _Mapping]] = ...) -> None: ...

class WebQuotedMessageReference(_message.Message):
    __slots__ = ("peer", "rid", "date", "seq", "story")
    PEER_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    STORY_FIELD_NUMBER: _ClassVar[int]
    peer: WebPeer
    rid: int
    date: WebInt64Value_1
    seq: WebInt64Value_1
    story: WebStoryType
    def __init__(self, peer: _Optional[_Union[WebPeer, _Mapping]] = ..., rid: _Optional[int] = ..., date: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., seq: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., story: _Optional[_Union[WebStoryType, _Mapping]] = ...) -> None: ...

class WebRaiseHand(_message.Message):
    __slots__ = ("userIdentity",)
    USERIDENTITY_FIELD_NUMBER: _ClassVar[int]
    userIdentity: str
    def __init__(self, userIdentity: _Optional[str] = ...) -> None: ...

class WebRawUpdate(_message.Message):
    __slots__ = ("type", "bytes")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    BYTES_FIELD_NUMBER: _ClassVar[int]
    type: WebStringValue
    bytes: bytes
    def __init__(self, type: _Optional[_Union[WebStringValue, _Mapping]] = ..., bytes: _Optional[bytes] = ...) -> None: ...

class WebReaction(_message.Message):
    __slots__ = ("users", "code", "cardinality", "ext")
    class ExtEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    USERS_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    CARDINALITY_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedScalarFieldContainer[int]
    code: str
    cardinality: WebInt64Value_1
    ext: _containers.ScalarMap[str, bytes]
    def __init__(self, users: _Optional[_Iterable[int]] = ..., code: _Optional[str] = ..., cardinality: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., ext: _Optional[_Mapping[str, bytes]] = ...) -> None: ...

class WebReactionsUpdate(_message.Message):
    __slots__ = ("peer", "rid", "reactions", "reactionByMe")
    PEER_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    REACTIONS_FIELD_NUMBER: _ClassVar[int]
    REACTIONBYME_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    rid: int
    reactions: _containers.RepeatedCompositeFieldContainer[WebReaction]
    reactionByMe: bool
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., rid: _Optional[int] = ..., reactions: _Optional[_Iterable[_Union[WebReaction, _Mapping]]] = ..., reactionByMe: _Optional[bool] = ...) -> None: ...

class WebReceiptMessage(_message.Message):
    __slots__ = ("message", "transferInfo")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TRANSFERINFO_FIELD_NUMBER: _ClassVar[int]
    message: WebExt
    transferInfo: WebExt
    def __init__(self, message: _Optional[_Union[WebExt, _Mapping]] = ..., transferInfo: _Optional[_Union[WebExt, _Mapping]] = ...) -> None: ...

class WebRepliesInfo(_message.Message):
    __slots__ = ("repliesCount", "recentRepliers", "lastMessage")
    REPLIESCOUNT_FIELD_NUMBER: _ClassVar[int]
    RECENTREPLIERS_FIELD_NUMBER: _ClassVar[int]
    LASTMESSAGE_FIELD_NUMBER: _ClassVar[int]
    repliesCount: int
    recentRepliers: _containers.RepeatedCompositeFieldContainer[WebUserPeer]
    lastMessage: WebMessageId
    def __init__(self, repliesCount: _Optional[int] = ..., recentRepliers: _Optional[_Iterable[_Union[WebUserPeer, _Mapping]]] = ..., lastMessage: _Optional[_Union[WebMessageId, _Mapping]] = ...) -> None: ...

class WebReplyKeyboardMarkup(_message.Message):
    __slots__ = ("listOfKeyboardList",)
    LISTOFKEYBOARDLIST_FIELD_NUMBER: _ClassVar[int]
    listOfKeyboardList: _containers.RepeatedCompositeFieldContainer[WebListOfKeyboardList]
    def __init__(self, listOfKeyboardList: _Optional[_Iterable[_Union[WebListOfKeyboardList, _Mapping]]] = ...) -> None: ...

class WebReplyKeyboardRemove(_message.Message):
    __slots__ = ("removeKeyboard", "selective")
    REMOVEKEYBOARD_FIELD_NUMBER: _ClassVar[int]
    SELECTIVE_FIELD_NUMBER: _ClassVar[int]
    removeKeyboard: bool
    selective: WebBoolValue_1
    def __init__(self, removeKeyboard: _Optional[bool] = ..., selective: _Optional[_Union[WebBoolValue_1, _Mapping]] = ...) -> None: ...

class WebRequestBankiAccessFor(_message.Message):
    __slots__ = ("bot", "service")
    BOT_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    bot: WebBot
    service: WebService
    def __init__(self, bot: _Optional[_Union[WebBot, _Mapping]] = ..., service: _Optional[_Union[WebService, _Mapping]] = ...) -> None: ...

class WebRequestChat(_message.Message):
    __slots__ = ("requestId", "chatIsChannel", "chatIsForum", "chatHasUsername", "chatIsCreated", "userAdministratorRights", "botAdministratorRights", "botIsMember")
    REQUESTID_FIELD_NUMBER: _ClassVar[int]
    CHATISCHANNEL_FIELD_NUMBER: _ClassVar[int]
    CHATISFORUM_FIELD_NUMBER: _ClassVar[int]
    CHATHASUSERNAME_FIELD_NUMBER: _ClassVar[int]
    CHATISCREATED_FIELD_NUMBER: _ClassVar[int]
    USERADMINISTRATORRIGHTS_FIELD_NUMBER: _ClassVar[int]
    BOTADMINISTRATORRIGHTS_FIELD_NUMBER: _ClassVar[int]
    BOTISMEMBER_FIELD_NUMBER: _ClassVar[int]
    requestId: int
    chatIsChannel: bool
    chatIsForum: bool
    chatHasUsername: bool
    chatIsCreated: bool
    userAdministratorRights: WebUserAdministratorRights
    botAdministratorRights: WebUserAdministratorRights
    botIsMember: bool
    def __init__(self, requestId: _Optional[int] = ..., chatIsChannel: _Optional[bool] = ..., chatIsForum: _Optional[bool] = ..., chatHasUsername: _Optional[bool] = ..., chatIsCreated: _Optional[bool] = ..., userAdministratorRights: _Optional[_Union[WebUserAdministratorRights, _Mapping]] = ..., botAdministratorRights: _Optional[_Union[WebUserAdministratorRights, _Mapping]] = ..., botIsMember: _Optional[bool] = ...) -> None: ...

class WebRequestLogin(_message.Message):
    __slots__ = ("bot", "service")
    BOT_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    bot: WebBot
    service: WebService
    def __init__(self, bot: _Optional[_Union[WebBot, _Mapping]] = ..., service: _Optional[_Union[WebService, _Mapping]] = ...) -> None: ...

class WebRequestPoll(_message.Message):
    __slots__ = ("type",)
    TYPE_FIELD_NUMBER: _ClassVar[int]
    type: str
    def __init__(self, type: _Optional[str] = ...) -> None: ...

class WebRequestUser(_message.Message):
    __slots__ = ("requestId", "userIsBot", "userIsPremium")
    REQUESTID_FIELD_NUMBER: _ClassVar[int]
    USERISBOT_FIELD_NUMBER: _ClassVar[int]
    USERISPREMIUM_FIELD_NUMBER: _ClassVar[int]
    requestId: int
    userIsBot: bool
    userIsPremium: bool
    def __init__(self, requestId: _Optional[int] = ..., userIsBot: _Optional[bool] = ..., userIsPremium: _Optional[bool] = ...) -> None: ...

class WebRgbColor(_message.Message):
    __slots__ = ("rgb",)
    RGB_FIELD_NUMBER: _ClassVar[int]
    rgb: int
    def __init__(self, rgb: _Optional[int] = ...) -> None: ...

class WebSavedGifsChanged(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebSearchAndCondition(_message.Message):
    __slots__ = ("andQuery",)
    ANDQUERY_FIELD_NUMBER: _ClassVar[int]
    andQuery: _containers.RepeatedCompositeFieldContainer[WebAndQuery]
    def __init__(self, andQuery: _Optional[_Iterable[_Union[WebAndQuery, _Mapping]]] = ...) -> None: ...

class WebSearchDate(_message.Message):
    __slots__ = ("date",)
    DATE_FIELD_NUMBER: _ClassVar[int]
    date: int
    def __init__(self, date: _Optional[int] = ...) -> None: ...

class WebSearchDocumentName(_message.Message):
    __slots__ = ("documentName",)
    DOCUMENTNAME_FIELD_NUMBER: _ClassVar[int]
    documentName: bytes
    def __init__(self, documentName: _Optional[bytes] = ...) -> None: ...

class WebSearchHasLink(_message.Message):
    __slots__ = ("hasLink",)
    HASLINK_FIELD_NUMBER: _ClassVar[int]
    hasLink: int
    def __init__(self, hasLink: _Optional[int] = ...) -> None: ...

class WebSearchOrCondition(_message.Message):
    __slots__ = ("orQuery",)
    ORQUERY_FIELD_NUMBER: _ClassVar[int]
    orQuery: _containers.RepeatedCompositeFieldContainer[WebAndQuery]
    def __init__(self, orQuery: _Optional[_Iterable[_Union[WebAndQuery, _Mapping]]] = ...) -> None: ...

class WebSearchPeerCondition(_message.Message):
    __slots__ = ("peer",)
    PEER_FIELD_NUMBER: _ClassVar[int]
    peer: WebPeer
    def __init__(self, peer: _Optional[_Union[WebPeer, _Mapping]] = ...) -> None: ...

class WebSearchPeerContentType(_message.Message):
    __slots__ = ("contentType",)
    CONTENTTYPE_FIELD_NUMBER: _ClassVar[int]
    contentType: int
    def __init__(self, contentType: _Optional[int] = ...) -> None: ...

class WebSearchPeerTypeCondition(_message.Message):
    __slots__ = ("peerType",)
    PEERTYPE_FIELD_NUMBER: _ClassVar[int]
    peerType: int
    def __init__(self, peerType: _Optional[int] = ...) -> None: ...

class WebSearchResult(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: WebT_U_34523
    def __init__(self, result: _Optional[_Union[WebT_U_34523, _Mapping]] = ...) -> None: ...

class WebSearchScopeCondition(_message.Message):
    __slots__ = ("scope",)
    SCOPE_FIELD_NUMBER: _ClassVar[int]
    scope: int
    def __init__(self, scope: _Optional[int] = ...) -> None: ...

class WebSearchSender(_message.Message):
    __slots__ = ("userId",)
    USERID_FIELD_NUMBER: _ClassVar[int]
    userId: int
    def __init__(self, userId: _Optional[int] = ...) -> None: ...

class WebSendMessageRequest(_message.Message):
    __slots__ = ("peer", "rid", "message", "isOnlyForUser", "quotedMessageReference", "exPeer", "isSilent", "threadId")
    PEER_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ISONLYFORUSER_FIELD_NUMBER: _ClassVar[int]
    QUOTEDMESSAGEREFERENCE_FIELD_NUMBER: _ClassVar[int]
    EXPEER_FIELD_NUMBER: _ClassVar[int]
    ISSILENT_FIELD_NUMBER: _ClassVar[int]
    THREADID_FIELD_NUMBER: _ClassVar[int]
    peer: WebPeer
    rid: int
    message: WebMessage
    isOnlyForUser: WebInt32Value
    quotedMessageReference: WebQuotedMessageReference
    exPeer: WebOutPeer
    isSilent: bool
    threadId: WebMessageId
    def __init__(self, peer: _Optional[_Union[WebPeer, _Mapping]] = ..., rid: _Optional[int] = ..., message: _Optional[_Union[WebMessage, _Mapping]] = ..., isOnlyForUser: _Optional[_Union[WebInt32Value, _Mapping]] = ..., quotedMessageReference: _Optional[_Union[WebQuotedMessageReference, _Mapping]] = ..., exPeer: _Optional[_Union[WebOutPeer, _Mapping]] = ..., isSilent: _Optional[bool] = ..., threadId: _Optional[_Union[WebMessageId, _Mapping]] = ...) -> None: ...

class WebSendMultiMediaMessageRequest(_message.Message):
    __slots__ = ("peer", "multiMedia", "repliedMessage", "groupedId")
    PEER_FIELD_NUMBER: _ClassVar[int]
    MULTIMEDIA_FIELD_NUMBER: _ClassVar[int]
    REPLIEDMESSAGE_FIELD_NUMBER: _ClassVar[int]
    GROUPEDID_FIELD_NUMBER: _ClassVar[int]
    peer: WebOutPeer
    multiMedia: _containers.RepeatedCompositeFieldContainer[WebMultiMedia]
    repliedMessage: WebQuotedMessageReference
    groupedId: int
    def __init__(self, peer: _Optional[_Union[WebOutPeer, _Mapping]] = ..., multiMedia: _Optional[_Iterable[_Union[WebMultiMedia, _Mapping]]] = ..., repliedMessage: _Optional[_Union[WebQuotedMessageReference, _Mapping]] = ..., groupedId: _Optional[int] = ...) -> None: ...

class WebSendType(_message.Message):
    __slots__ = ("type",)
    TYPE_FIELD_NUMBER: _ClassVar[int]
    type: int
    def __init__(self, type: _Optional[int] = ...) -> None: ...

class WebService(_message.Message):
    __slots__ = ("serviceKey", "serviceFaName", "serviceEnName")
    SERVICEKEY_FIELD_NUMBER: _ClassVar[int]
    SERVICEFANAME_FIELD_NUMBER: _ClassVar[int]
    SERVICEENNAME_FIELD_NUMBER: _ClassVar[int]
    serviceKey: str
    serviceFaName: str
    serviceEnName: str
    def __init__(self, serviceKey: _Optional[str] = ..., serviceFaName: _Optional[str] = ..., serviceEnName: _Optional[str] = ...) -> None: ...

class WebServiceExAnonymousContact(_message.Message):
    __slots__ = ("desc",)
    DESC_FIELD_NUMBER: _ClassVar[int]
    desc: WebStringValue
    def __init__(self, desc: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebServiceExBecameOrphaned(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebServiceExCallRecordStateChanged(_message.Message):
    __slots__ = ("starterUserId", "isStarted")
    STARTERUSERID_FIELD_NUMBER: _ClassVar[int]
    ISSTARTED_FIELD_NUMBER: _ClassVar[int]
    starterUserId: int
    isStarted: bool
    def __init__(self, starterUserId: _Optional[int] = ..., isStarted: _Optional[bool] = ...) -> None: ...

class WebServiceExChangedAbout(_message.Message):
    __slots__ = ("about",)
    ABOUT_FIELD_NUMBER: _ClassVar[int]
    about: WebStringValue
    def __init__(self, about: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebServiceExChangedAvatar(_message.Message):
    __slots__ = ("avatar",)
    AVATAR_FIELD_NUMBER: _ClassVar[int]
    avatar: WebAvatar
    def __init__(self, avatar: _Optional[_Union[WebAvatar, _Mapping]] = ...) -> None: ...

class WebServiceExChangedNick(_message.Message):
    __slots__ = ("nick",)
    NICK_FIELD_NUMBER: _ClassVar[int]
    nick: WebStringValue
    def __init__(self, nick: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebServiceExChangedTitle(_message.Message):
    __slots__ = ("title",)
    TITLE_FIELD_NUMBER: _ClassVar[int]
    title: str
    def __init__(self, title: _Optional[str] = ...) -> None: ...

class WebServiceExChangedTopic(_message.Message):
    __slots__ = ("topic",)
    TOPIC_FIELD_NUMBER: _ClassVar[int]
    topic: WebStringValue
    def __init__(self, topic: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebServiceExChatArchived(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebServiceExChatRestored(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebServiceExContactRegistered(_message.Message):
    __slots__ = ("uid",)
    UID_FIELD_NUMBER: _ClassVar[int]
    uid: int
    def __init__(self, uid: _Optional[int] = ...) -> None: ...

class WebServiceExGiftPacketOpened(_message.Message):
    __slots__ = ("userId", "msgRid", "msgDate")
    USERID_FIELD_NUMBER: _ClassVar[int]
    MSGRID_FIELD_NUMBER: _ClassVar[int]
    MSGDATE_FIELD_NUMBER: _ClassVar[int]
    userId: int
    msgRid: int
    msgDate: int
    def __init__(self, userId: _Optional[int] = ..., msgRid: _Optional[int] = ..., msgDate: _Optional[int] = ...) -> None: ...

class WebServiceExGiftPacketOpenedCompact(_message.Message):
    __slots__ = ("lastUserId", "othersCount", "msgRid", "msgDate")
    LASTUSERID_FIELD_NUMBER: _ClassVar[int]
    OTHERSCOUNT_FIELD_NUMBER: _ClassVar[int]
    MSGRID_FIELD_NUMBER: _ClassVar[int]
    MSGDATE_FIELD_NUMBER: _ClassVar[int]
    lastUserId: int
    othersCount: int
    msgRid: int
    msgDate: int
    def __init__(self, lastUserId: _Optional[int] = ..., othersCount: _Optional[int] = ..., msgRid: _Optional[int] = ..., msgDate: _Optional[int] = ...) -> None: ...

class WebServiceExGroupCallEnded(_message.Message):
    __slots__ = ("groupCall", "missed", "extra", "ext")
    class ExtraEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    class ExtEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    GROUPCALL_FIELD_NUMBER: _ClassVar[int]
    MISSED_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    groupCall: WebGroupCall
    missed: bool
    extra: _containers.ScalarMap[str, bytes]
    ext: _containers.ScalarMap[str, bytes]
    def __init__(self, groupCall: _Optional[_Union[WebGroupCall, _Mapping]] = ..., missed: _Optional[bool] = ..., extra: _Optional[_Mapping[str, bytes]] = ..., ext: _Optional[_Mapping[str, bytes]] = ...) -> None: ...

class WebServiceExGroupCallStarted(_message.Message):
    __slots__ = ("groupCall", "extra", "ext")
    class ExtraEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    class ExtEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    GROUPCALL_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    groupCall: WebGroupCall
    extra: _containers.ScalarMap[str, bytes]
    ext: _containers.ScalarMap[str, bytes]
    def __init__(self, groupCall: _Optional[_Union[WebGroupCall, _Mapping]] = ..., extra: _Optional[_Mapping[str, bytes]] = ..., ext: _Optional[_Mapping[str, bytes]] = ...) -> None: ...

class WebServiceExGroupCreated(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebServiceExMiniAppDataSent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebServiceExNewUserWelcome(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebServiceExPassportDataSent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebServiceExPhoneCall(_message.Message):
    __slots__ = ("duration", "startDate", "discardReason", "isVideo", "extra", "ext", "call")
    class ExtraEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    class ExtEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    DURATION_FIELD_NUMBER: _ClassVar[int]
    STARTDATE_FIELD_NUMBER: _ClassVar[int]
    DISCARDREASON_FIELD_NUMBER: _ClassVar[int]
    ISVIDEO_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    CALL_FIELD_NUMBER: _ClassVar[int]
    duration: int
    startDate: WebInt64Value_1
    discardReason: int
    isVideo: WebBoolValue_1
    extra: _containers.ScalarMap[str, bytes]
    ext: _containers.ScalarMap[str, bytes]
    call: WebCall
    def __init__(self, duration: _Optional[int] = ..., startDate: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., discardReason: _Optional[int] = ..., isVideo: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., extra: _Optional[_Mapping[str, bytes]] = ..., ext: _Optional[_Mapping[str, bytes]] = ..., call: _Optional[_Union[WebCall, _Mapping]] = ...) -> None: ...

class WebServiceExPhoneMissed(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebServiceExTopicCreated(_message.Message):
    __slots__ = ("title",)
    TITLE_FIELD_NUMBER: _ClassVar[int]
    title: WebStringValue
    def __init__(self, title: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebServiceExUserInvited(_message.Message):
    __slots__ = ("invitedUid",)
    INVITEDUID_FIELD_NUMBER: _ClassVar[int]
    invitedUid: int
    def __init__(self, invitedUid: _Optional[int] = ...) -> None: ...

class WebServiceExUserJoined(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebServiceExUserKicked(_message.Message):
    __slots__ = ("kickedUid",)
    KICKEDUID_FIELD_NUMBER: _ClassVar[int]
    kickedUid: int
    def __init__(self, kickedUid: _Optional[int] = ...) -> None: ...

class WebServiceExUserLeft(_message.Message):
    __slots__ = ("leftUid",)
    LEFTUID_FIELD_NUMBER: _ClassVar[int]
    leftUid: int
    def __init__(self, leftUid: _Optional[int] = ...) -> None: ...

class WebServiceMessage(_message.Message):
    __slots__ = ("text", "ext")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    ext: WebT_ev_95053
    def __init__(self, text: _Optional[str] = ..., ext: _Optional[_Union[WebT_ev_95053, _Mapping]] = ...) -> None: ...

class WebShowSnackBarAction(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class WebSmallImage(_message.Message):
    __slots__ = ("fileLocation", "width", "height", "fileSize")
    FILELOCATION_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FILESIZE_FIELD_NUMBER: _ClassVar[int]
    fileLocation: WebFileLocation
    width: int
    height: int
    fileSize: int
    def __init__(self, fileLocation: _Optional[_Union[WebFileLocation, _Mapping]] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., fileSize: _Optional[int] = ...) -> None: ...

class WebStartLive(_message.Message):
    __slots__ = ("info",)
    INFO_FIELD_NUMBER: _ClassVar[int]
    info: WebInfo
    def __init__(self, info: _Optional[_Union[WebInfo, _Mapping]] = ...) -> None: ...

class WebState(_message.Message):
    __slots__ = ("groupPeer", "seq")
    GROUPPEER_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    groupPeer: WebGroupPeer
    seq: int
    def __init__(self, groupPeer: _Optional[_Union[WebGroupPeer, _Mapping]] = ..., seq: _Optional[int] = ...) -> None: ...

class WebSticker(_message.Message):
    __slots__ = ("id", "emoji", "image128", "image512", "image256")
    ID_FIELD_NUMBER: _ClassVar[int]
    EMOJI_FIELD_NUMBER: _ClassVar[int]
    IMAGE128_FIELD_NUMBER: _ClassVar[int]
    IMAGE512_FIELD_NUMBER: _ClassVar[int]
    IMAGE256_FIELD_NUMBER: _ClassVar[int]
    id: int
    emoji: WebStringValue
    image128: WebImageLocation
    image512: WebImageLocation
    image256: WebImageLocation
    def __init__(self, id: _Optional[int] = ..., emoji: _Optional[_Union[WebStringValue, _Mapping]] = ..., image128: _Optional[_Union[WebImageLocation, _Mapping]] = ..., image512: _Optional[_Union[WebImageLocation, _Mapping]] = ..., image256: _Optional[_Union[WebImageLocation, _Mapping]] = ...) -> None: ...

class WebStickerCollectionsChanged(_message.Message):
    __slots__ = ("collections",)
    COLLECTIONS_FIELD_NUMBER: _ClassVar[int]
    collections: _containers.RepeatedCompositeFieldContainer[WebCollection]
    def __init__(self, collections: _Optional[_Iterable[_Union[WebCollection, _Mapping]]] = ...) -> None: ...

class WebStickerMessage(_message.Message):
    __slots__ = ("stickerId", "fastPreview", "image512", "image256", "stickerCollectionId", "stickerCollectionAccessHash")
    STICKERID_FIELD_NUMBER: _ClassVar[int]
    FASTPREVIEW_FIELD_NUMBER: _ClassVar[int]
    IMAGE512_FIELD_NUMBER: _ClassVar[int]
    IMAGE256_FIELD_NUMBER: _ClassVar[int]
    STICKERCOLLECTIONID_FIELD_NUMBER: _ClassVar[int]
    STICKERCOLLECTIONACCESSHASH_FIELD_NUMBER: _ClassVar[int]
    stickerId: WebInt32Value
    fastPreview: WebBytesValue
    image512: WebImageLocation
    image256: WebImageLocation
    stickerCollectionId: WebInt32Value
    stickerCollectionAccessHash: WebInt64Value_1
    def __init__(self, stickerId: _Optional[_Union[WebInt32Value, _Mapping]] = ..., fastPreview: _Optional[_Union[WebBytesValue, _Mapping]] = ..., image512: _Optional[_Union[WebImageLocation, _Mapping]] = ..., image256: _Optional[_Union[WebImageLocation, _Mapping]] = ..., stickerCollectionId: _Optional[_Union[WebInt32Value, _Mapping]] = ..., stickerCollectionAccessHash: _Optional[_Union[WebInt64Value_1, _Mapping]] = ...) -> None: ...

class WebStickerPacksChanged(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebStoryType(_message.Message):
    __slots__ = ("storyId", "owner")
    STORYID_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    storyId: str
    owner: WebOutPeer
    def __init__(self, storyId: _Optional[str] = ..., owner: _Optional[_Union[WebOutPeer, _Mapping]] = ...) -> None: ...

class WebStreamedMessage(_message.Message):
    __slots__ = ("message", "messageStreamStatus")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    MESSAGESTREAMSTATUS_FIELD_NUMBER: _ClassVar[int]
    message: WebMessage
    messageStreamStatus: int
    def __init__(self, message: _Optional[_Union[WebMessage, _Mapping]] = ..., messageStreamStatus: _Optional[int] = ...) -> None: ...

class WebStringValue(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class WebStyle(_message.Message):
    __slots__ = ("showParagraph", "paragraphColor", "bgColor")
    SHOWPARAGRAPH_FIELD_NUMBER: _ClassVar[int]
    PARAGRAPHCOLOR_FIELD_NUMBER: _ClassVar[int]
    BGCOLOR_FIELD_NUMBER: _ClassVar[int]
    showParagraph: WebBoolValue_1
    paragraphColor: WebParagraphColor
    bgColor: WebParagraphColor
    def __init__(self, showParagraph: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., paragraphColor: _Optional[_Union[WebParagraphColor, _Mapping]] = ..., bgColor: _Optional[_Union[WebParagraphColor, _Mapping]] = ...) -> None: ...

class WebSwitchInlineQueryChosenChat(_message.Message):
    __slots__ = ("query", "allowUserChats", "allowBotChats", "allowGroupChats", "allowChannelChats")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    ALLOWUSERCHATS_FIELD_NUMBER: _ClassVar[int]
    ALLOWBOTCHATS_FIELD_NUMBER: _ClassVar[int]
    ALLOWGROUPCHATS_FIELD_NUMBER: _ClassVar[int]
    ALLOWCHANNELCHATS_FIELD_NUMBER: _ClassVar[int]
    query: str
    allowUserChats: bool
    allowBotChats: bool
    allowGroupChats: bool
    allowChannelChats: bool
    def __init__(self, query: _Optional[str] = ..., allowUserChats: _Optional[bool] = ..., allowBotChats: _Optional[bool] = ..., allowGroupChats: _Optional[bool] = ..., allowChannelChats: _Optional[bool] = ...) -> None: ...

class WebT_d_46216(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: WebValue
    def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[WebValue, _Mapping]] = ...) -> None: ...

class WebT_d_61936(_message.Message):
    __slots__ = ("terminationSignal", "textChunk")
    TERMINATIONSIGNAL_FIELD_NUMBER: _ClassVar[int]
    TEXTCHUNK_FIELD_NUMBER: _ClassVar[int]
    terminationSignal: WebTerminationSignal
    textChunk: WebTextChunk
    def __init__(self, terminationSignal: _Optional[_Union[WebTerminationSignal, _Mapping]] = ..., textChunk: _Optional[_Union[WebTextChunk, _Mapping]] = ...) -> None: ...

class WebT_E_95053(_message.Message):
    __slots__ = ("url", "secureUrl", "type", "height", "width")
    URL_FIELD_NUMBER: _ClassVar[int]
    SECUREURL_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    url: str
    secureUrl: str
    type: str
    height: int
    width: int
    def __init__(self, url: _Optional[str] = ..., secureUrl: _Optional[str] = ..., type: _Optional[str] = ..., height: _Optional[int] = ..., width: _Optional[int] = ...) -> None: ...

class WebT_ev_95053(_message.Message):
    __slots__ = ("serviceExBecameOrphaned", "serviceExChangedAbout", "serviceExChangedAvatar", "serviceExChangedNick", "serviceExChangedTitle", "serviceExChangedTopic", "serviceExChatArchived", "serviceExChatRestored", "serviceExContactRegistered", "serviceExGroupCreated", "serviceExPhoneCall", "serviceExPhoneMissed", "serviceExUserInvited", "serviceExUserJoined", "serviceExUserKicked", "serviceExUserLeft", "serviceExGiftPacketOpened", "serviceExGiftPacketOpenedCompact", "serviceExNewUserWelcome", "serviceExGroupCallStarted", "serviceExGroupCallEnded", "serviceExCallRecordStateChanged", "serviceExMiniAppDataSent", "serviceExAnonymousContact", "serviceExPassportDataSent", "serviceExTopicCreated")
    SERVICEEXBECAMEORPHANED_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXCHANGEDABOUT_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXCHANGEDAVATAR_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXCHANGEDNICK_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXCHANGEDTITLE_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXCHANGEDTOPIC_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXCHATARCHIVED_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXCHATRESTORED_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXCONTACTREGISTERED_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXGROUPCREATED_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXPHONECALL_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXPHONEMISSED_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXUSERINVITED_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXUSERJOINED_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXUSERKICKED_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXUSERLEFT_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXGIFTPACKETOPENED_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXGIFTPACKETOPENEDCOMPACT_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXNEWUSERWELCOME_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXGROUPCALLSTARTED_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXGROUPCALLENDED_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXCALLRECORDSTATECHANGED_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXMINIAPPDATASENT_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXANONYMOUSCONTACT_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXPASSPORTDATASENT_FIELD_NUMBER: _ClassVar[int]
    SERVICEEXTOPICCREATED_FIELD_NUMBER: _ClassVar[int]
    serviceExBecameOrphaned: WebServiceExBecameOrphaned
    serviceExChangedAbout: WebServiceExChangedAbout
    serviceExChangedAvatar: WebServiceExChangedAvatar
    serviceExChangedNick: WebServiceExChangedNick
    serviceExChangedTitle: WebServiceExChangedTitle
    serviceExChangedTopic: WebServiceExChangedTopic
    serviceExChatArchived: WebServiceExChatArchived
    serviceExChatRestored: WebServiceExChatRestored
    serviceExContactRegistered: WebServiceExContactRegistered
    serviceExGroupCreated: WebServiceExGroupCreated
    serviceExPhoneCall: WebServiceExPhoneCall
    serviceExPhoneMissed: WebServiceExPhoneMissed
    serviceExUserInvited: WebServiceExUserInvited
    serviceExUserJoined: WebServiceExUserJoined
    serviceExUserKicked: WebServiceExUserKicked
    serviceExUserLeft: WebServiceExUserLeft
    serviceExGiftPacketOpened: WebServiceExGiftPacketOpened
    serviceExGiftPacketOpenedCompact: WebServiceExGiftPacketOpenedCompact
    serviceExNewUserWelcome: WebServiceExNewUserWelcome
    serviceExGroupCallStarted: WebServiceExGroupCallStarted
    serviceExGroupCallEnded: WebServiceExGroupCallEnded
    serviceExCallRecordStateChanged: WebServiceExCallRecordStateChanged
    serviceExMiniAppDataSent: WebServiceExMiniAppDataSent
    serviceExAnonymousContact: WebServiceExAnonymousContact
    serviceExPassportDataSent: WebServiceExPassportDataSent
    serviceExTopicCreated: WebServiceExTopicCreated
    def __init__(self, serviceExBecameOrphaned: _Optional[_Union[WebServiceExBecameOrphaned, _Mapping]] = ..., serviceExChangedAbout: _Optional[_Union[WebServiceExChangedAbout, _Mapping]] = ..., serviceExChangedAvatar: _Optional[_Union[WebServiceExChangedAvatar, _Mapping]] = ..., serviceExChangedNick: _Optional[_Union[WebServiceExChangedNick, _Mapping]] = ..., serviceExChangedTitle: _Optional[_Union[WebServiceExChangedTitle, _Mapping]] = ..., serviceExChangedTopic: _Optional[_Union[WebServiceExChangedTopic, _Mapping]] = ..., serviceExChatArchived: _Optional[_Union[WebServiceExChatArchived, _Mapping]] = ..., serviceExChatRestored: _Optional[_Union[WebServiceExChatRestored, _Mapping]] = ..., serviceExContactRegistered: _Optional[_Union[WebServiceExContactRegistered, _Mapping]] = ..., serviceExGroupCreated: _Optional[_Union[WebServiceExGroupCreated, _Mapping]] = ..., serviceExPhoneCall: _Optional[_Union[WebServiceExPhoneCall, _Mapping]] = ..., serviceExPhoneMissed: _Optional[_Union[WebServiceExPhoneMissed, _Mapping]] = ..., serviceExUserInvited: _Optional[_Union[WebServiceExUserInvited, _Mapping]] = ..., serviceExUserJoined: _Optional[_Union[WebServiceExUserJoined, _Mapping]] = ..., serviceExUserKicked: _Optional[_Union[WebServiceExUserKicked, _Mapping]] = ..., serviceExUserLeft: _Optional[_Union[WebServiceExUserLeft, _Mapping]] = ..., serviceExGiftPacketOpened: _Optional[_Union[WebServiceExGiftPacketOpened, _Mapping]] = ..., serviceExGiftPacketOpenedCompact: _Optional[_Union[WebServiceExGiftPacketOpenedCompact, _Mapping]] = ..., serviceExNewUserWelcome: _Optional[_Union[WebServiceExNewUserWelcome, _Mapping]] = ..., serviceExGroupCallStarted: _Optional[_Union[WebServiceExGroupCallStarted, _Mapping]] = ..., serviceExGroupCallEnded: _Optional[_Union[WebServiceExGroupCallEnded, _Mapping]] = ..., serviceExCallRecordStateChanged: _Optional[_Union[WebServiceExCallRecordStateChanged, _Mapping]] = ..., serviceExMiniAppDataSent: _Optional[_Union[WebServiceExMiniAppDataSent, _Mapping]] = ..., serviceExAnonymousContact: _Optional[_Union[WebServiceExAnonymousContact, _Mapping]] = ..., serviceExPassportDataSent: _Optional[_Union[WebServiceExPassportDataSent, _Mapping]] = ..., serviceExTopicCreated: _Optional[_Union[WebServiceExTopicCreated, _Mapping]] = ...) -> None: ...

class WebT_f_68220(_message.Message):
    __slots__ = ("customOpenUrlAction", "customDoNothingAction")
    CUSTOMOPENURLACTION_FIELD_NUMBER: _ClassVar[int]
    CUSTOMDONOTHINGACTION_FIELD_NUMBER: _ClassVar[int]
    customOpenUrlAction: WebCustomOpenUrlAction
    customDoNothingAction: WebCustomDoNothingAction
    def __init__(self, customOpenUrlAction: _Optional[_Union[WebCustomOpenUrlAction, _Mapping]] = ..., customDoNothingAction: _Optional[_Union[WebCustomDoNothingAction, _Mapping]] = ...) -> None: ...

class WebT_I_(_message.Message):
    __slots__ = ("peer", "title", "description", "membersCount", "dateCreated", "creator", "isPublic", "isJoined")
    PEER_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MEMBERSCOUNT_FIELD_NUMBER: _ClassVar[int]
    DATECREATED_FIELD_NUMBER: _ClassVar[int]
    CREATOR_FIELD_NUMBER: _ClassVar[int]
    ISPUBLIC_FIELD_NUMBER: _ClassVar[int]
    ISJOINED_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    title: bytes
    description: WebStringValue
    membersCount: WebInt32Value
    dateCreated: WebInt64Value_1
    creator: WebInt32Value
    isPublic: WebBoolValue_1
    isJoined: WebBoolValue_1
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., title: _Optional[bytes] = ..., description: _Optional[_Union[WebStringValue, _Mapping]] = ..., membersCount: _Optional[_Union[WebInt32Value, _Mapping]] = ..., dateCreated: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., creator: _Optional[_Union[WebInt32Value, _Mapping]] = ..., isPublic: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., isJoined: _Optional[_Union[WebBoolValue_1, _Mapping]] = ...) -> None: ...

class WebT_iG_95053(_message.Message):
    __slots__ = ("title", "description", "agreeButton", "disagreeButton")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    AGREEBUTTON_FIELD_NUMBER: _ClassVar[int]
    DISAGREEBUTTON_FIELD_NUMBER: _ClassVar[int]
    title: str
    description: str
    agreeButton: str
    disagreeButton: str
    def __init__(self, title: _Optional[str] = ..., description: _Optional[str] = ..., agreeButton: _Optional[str] = ..., disagreeButton: _Optional[str] = ...) -> None: ...

class WebT_LnR(_message.Message):
    __slots__ = ("documentExPhoto", "documentExVideo", "documentExVoice", "documentExGif", "documentExAudio")
    DOCUMENTEXPHOTO_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTEXVIDEO_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTEXVOICE_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTEXGIF_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTEXAUDIO_FIELD_NUMBER: _ClassVar[int]
    documentExPhoto: WebDocumentExPhoto
    documentExVideo: WebDocumentExVideo
    documentExVoice: WebDocumentExVoice
    documentExGif: WebDocumentExGif
    documentExAudio: WebDocumentExAudio
    def __init__(self, documentExPhoto: _Optional[_Union[WebDocumentExPhoto, _Mapping]] = ..., documentExVideo: _Optional[_Union[WebDocumentExVideo, _Mapping]] = ..., documentExVoice: _Optional[_Union[WebDocumentExVoice, _Mapping]] = ..., documentExGif: _Optional[_Union[WebDocumentExGif, _Mapping]] = ..., documentExAudio: _Optional[_Union[WebDocumentExAudio, _Mapping]] = ...) -> None: ...

class WebT_LWL(_message.Message):
    __slots__ = ("dates",)
    DATES_FIELD_NUMBER: _ClassVar[int]
    dates: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, dates: _Optional[_Iterable[int]] = ...) -> None: ...

class WebT_n4(_message.Message):
    __slots__ = ("id", "accessHash", "name", "localName", "nick", "avatar", "about", "contactInfo", "isBot", "sex", "exInfo", "botCommands", "isBlocked", "isDeleted", "isContact", "ext", "preferredLanguages", "timeZone", "defaultBankAccount", "defaultCardNumber", "puppeteer", "createdAt", "privacyBarMode", "privacyAllowedToInvite", "botExInfo")
    class ExtEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    ACCESSHASH_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LOCALNAME_FIELD_NUMBER: _ClassVar[int]
    NICK_FIELD_NUMBER: _ClassVar[int]
    AVATAR_FIELD_NUMBER: _ClassVar[int]
    ABOUT_FIELD_NUMBER: _ClassVar[int]
    CONTACTINFO_FIELD_NUMBER: _ClassVar[int]
    ISBOT_FIELD_NUMBER: _ClassVar[int]
    SEX_FIELD_NUMBER: _ClassVar[int]
    EXINFO_FIELD_NUMBER: _ClassVar[int]
    BOTCOMMANDS_FIELD_NUMBER: _ClassVar[int]
    ISBLOCKED_FIELD_NUMBER: _ClassVar[int]
    ISDELETED_FIELD_NUMBER: _ClassVar[int]
    ISCONTACT_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    PREFERREDLANGUAGES_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    DEFAULTBANKACCOUNT_FIELD_NUMBER: _ClassVar[int]
    DEFAULTCARDNUMBER_FIELD_NUMBER: _ClassVar[int]
    PUPPETEER_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    PRIVACYBARMODE_FIELD_NUMBER: _ClassVar[int]
    PRIVACYALLOWEDTOINVITE_FIELD_NUMBER: _ClassVar[int]
    BOTEXINFO_FIELD_NUMBER: _ClassVar[int]
    id: int
    accessHash: int
    name: str
    localName: WebStringValue
    nick: WebStringValue
    avatar: WebAvatar
    about: WebStringValue
    contactInfo: _containers.RepeatedCompositeFieldContainer[WebContactInfo]
    isBot: WebBoolValue_1
    sex: int
    exInfo: WebExInfo
    botCommands: _containers.RepeatedCompositeFieldContainer[WebBotCommand]
    isBlocked: WebBoolValue_1
    isDeleted: WebBoolValue_1
    isContact: WebBoolValue_1
    ext: _containers.ScalarMap[str, bytes]
    preferredLanguages: _containers.RepeatedScalarFieldContainer[str]
    timeZone: WebStringValue
    defaultBankAccount: WebStringValue
    defaultCardNumber: WebStringValue
    puppeteer: int
    createdAt: WebInt64Value_1
    privacyBarMode: int
    privacyAllowedToInvite: WebBoolValue_1
    botExInfo: WebBotExInfo
    def __init__(self, id: _Optional[int] = ..., accessHash: _Optional[int] = ..., name: _Optional[str] = ..., localName: _Optional[_Union[WebStringValue, _Mapping]] = ..., nick: _Optional[_Union[WebStringValue, _Mapping]] = ..., avatar: _Optional[_Union[WebAvatar, _Mapping]] = ..., about: _Optional[_Union[WebStringValue, _Mapping]] = ..., contactInfo: _Optional[_Iterable[_Union[WebContactInfo, _Mapping]]] = ..., isBot: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., sex: _Optional[int] = ..., exInfo: _Optional[_Union[WebExInfo, _Mapping]] = ..., botCommands: _Optional[_Iterable[_Union[WebBotCommand, _Mapping]]] = ..., isBlocked: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., isDeleted: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., isContact: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., ext: _Optional[_Mapping[str, bytes]] = ..., preferredLanguages: _Optional[_Iterable[str]] = ..., timeZone: _Optional[_Union[WebStringValue, _Mapping]] = ..., defaultBankAccount: _Optional[_Union[WebStringValue, _Mapping]] = ..., defaultCardNumber: _Optional[_Union[WebStringValue, _Mapping]] = ..., puppeteer: _Optional[int] = ..., createdAt: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., privacyBarMode: _Optional[int] = ..., privacyAllowedToInvite: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., botExInfo: _Optional[_Union[WebBotExInfo, _Mapping]] = ...) -> None: ...

class WebT_nK_95053(_message.Message):
    __slots__ = ("peer", "counter", "date", "exInfo", "firstUnreadDate", "markedAsUnread")
    PEER_FIELD_NUMBER: _ClassVar[int]
    COUNTER_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    EXINFO_FIELD_NUMBER: _ClassVar[int]
    FIRSTUNREADDATE_FIELD_NUMBER: _ClassVar[int]
    MARKEDASUNREAD_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    counter: int
    date: int
    exInfo: WebExInfo
    firstUnreadDate: WebInt64Value_1
    markedAsUnread: WebBoolValue_1
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., counter: _Optional[int] = ..., date: _Optional[int] = ..., exInfo: _Optional[_Union[WebExInfo, _Mapping]] = ..., firstUnreadDate: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., markedAsUnread: _Optional[_Union[WebBoolValue_1, _Mapping]] = ...) -> None: ...

class WebT_t6_95053(_message.Message):
    __slots__ = ("id", "transactionName", "transactionChannel", "transactionDate", "transactionAmountWithSign", "transactionType", "categoryId", "comment", "brno", "transactionTrace", "hyperLink")
    ID_FIELD_NUMBER: _ClassVar[int]
    TRANSACTIONNAME_FIELD_NUMBER: _ClassVar[int]
    TRANSACTIONCHANNEL_FIELD_NUMBER: _ClassVar[int]
    TRANSACTIONDATE_FIELD_NUMBER: _ClassVar[int]
    TRANSACTIONAMOUNTWITHSIGN_FIELD_NUMBER: _ClassVar[int]
    TRANSACTIONTYPE_FIELD_NUMBER: _ClassVar[int]
    CATEGORYID_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    BRNO_FIELD_NUMBER: _ClassVar[int]
    TRANSACTIONTRACE_FIELD_NUMBER: _ClassVar[int]
    HYPERLINK_FIELD_NUMBER: _ClassVar[int]
    id: int
    transactionName: str
    transactionChannel: str
    transactionDate: int
    transactionAmountWithSign: str
    transactionType: str
    categoryId: int
    comment: str
    brno: int
    transactionTrace: str
    hyperLink: WebInt32Value
    def __init__(self, id: _Optional[int] = ..., transactionName: _Optional[str] = ..., transactionChannel: _Optional[str] = ..., transactionDate: _Optional[int] = ..., transactionAmountWithSign: _Optional[str] = ..., transactionType: _Optional[str] = ..., categoryId: _Optional[int] = ..., comment: _Optional[str] = ..., brno: _Optional[int] = ..., transactionTrace: _Optional[str] = ..., hyperLink: _Optional[_Union[WebInt32Value, _Mapping]] = ...) -> None: ...

class WebT_THn(_message.Message):
    __slots__ = ("mId", "views")
    MID_FIELD_NUMBER: _ClassVar[int]
    VIEWS_FIELD_NUMBER: _ClassVar[int]
    mId: WebMessageId
    views: WebInt64Value_1
    def __init__(self, mId: _Optional[_Union[WebMessageId, _Mapping]] = ..., views: _Optional[_Union[WebInt64Value_1, _Mapping]] = ...) -> None: ...

class WebT_TS(_message.Message):
    __slots__ = ("maxGroupSize",)
    MAXGROUPSIZE_FIELD_NUMBER: _ClassVar[int]
    maxGroupSize: int
    def __init__(self, maxGroupSize: _Optional[int] = ...) -> None: ...

class WebT_tW_88717(_message.Message):
    __slots__ = ("state", "updates", "needMore", "tooLong", "newUpdates")
    STATE_FIELD_NUMBER: _ClassVar[int]
    UPDATES_FIELD_NUMBER: _ClassVar[int]
    NEEDMORE_FIELD_NUMBER: _ClassVar[int]
    TOOLONG_FIELD_NUMBER: _ClassVar[int]
    NEWUPDATES_FIELD_NUMBER: _ClassVar[int]
    state: WebState
    updates: _containers.RepeatedCompositeFieldContainer[WebUpdate]
    needMore: int
    tooLong: WebBoolValue_1
    newUpdates: _containers.RepeatedCompositeFieldContainer[WebNewUpdate]
    def __init__(self, state: _Optional[_Union[WebState, _Mapping]] = ..., updates: _Optional[_Iterable[_Union[WebUpdate, _Mapping]]] = ..., needMore: _Optional[int] = ..., tooLong: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., newUpdates: _Optional[_Iterable[_Union[WebNewUpdate, _Mapping]]] = ...) -> None: ...

class WebT_U_34523(_message.Message):
    __slots__ = ("peer", "rid", "date", "senderId", "content", "messageContainer")
    PEER_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    SENDERID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    MESSAGECONTAINER_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    rid: int
    date: int
    senderId: int
    content: WebMessage
    messageContainer: WebHistory
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., rid: _Optional[int] = ..., date: _Optional[int] = ..., senderId: _Optional[int] = ..., content: _Optional[_Union[WebMessage, _Mapping]] = ..., messageContainer: _Optional[_Union[WebHistory, _Mapping]] = ...) -> None: ...

class WebT_w_59727(_message.Message):
    __slots__ = ("fileLocation", "fileSize", "mimeType", "fileName", "mediaExtra")
    FILELOCATION_FIELD_NUMBER: _ClassVar[int]
    FILESIZE_FIELD_NUMBER: _ClassVar[int]
    MIMETYPE_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    MEDIAEXTRA_FIELD_NUMBER: _ClassVar[int]
    fileLocation: WebFileLocation
    fileSize: int
    mimeType: str
    fileName: str
    mediaExtra: WebMediaExtra
    def __init__(self, fileLocation: _Optional[_Union[WebFileLocation, _Mapping]] = ..., fileSize: _Optional[int] = ..., mimeType: _Optional[str] = ..., fileName: _Optional[str] = ..., mediaExtra: _Optional[_Union[WebMediaExtra, _Mapping]] = ...) -> None: ...

class WebT_wpU(_message.Message):
    __slots__ = ("title", "key", "dialogs")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    DIALOGS_FIELD_NUMBER: _ClassVar[int]
    title: str
    key: str
    dialogs: _containers.RepeatedCompositeFieldContainer[WebT_nK_95053]
    def __init__(self, title: _Optional[str] = ..., key: _Optional[str] = ..., dialogs: _Optional[_Iterable[_Union[WebT_nK_95053, _Mapping]]] = ...) -> None: ...

class WebT_Z_95053(_message.Message):
    __slots__ = ("textCommand", "textExMarkdown", "textModernMessage", "textLinkPreview")
    TEXTCOMMAND_FIELD_NUMBER: _ClassVar[int]
    TEXTEXMARKDOWN_FIELD_NUMBER: _ClassVar[int]
    TEXTMODERNMESSAGE_FIELD_NUMBER: _ClassVar[int]
    TEXTLINKPREVIEW_FIELD_NUMBER: _ClassVar[int]
    textCommand: WebTextCommand
    textExMarkdown: WebTextExMarkdown
    textModernMessage: WebTextModernMessage
    textLinkPreview: WebTextLinkPreview
    def __init__(self, textCommand: _Optional[_Union[WebTextCommand, _Mapping]] = ..., textExMarkdown: _Optional[_Union[WebTextExMarkdown, _Mapping]] = ..., textModernMessage: _Optional[_Union[WebTextModernMessage, _Mapping]] = ..., textLinkPreview: _Optional[_Union[WebTextLinkPreview, _Mapping]] = ...) -> None: ...

class WebTemplateMessage(_message.Message):
    __slots__ = ("generalMessage", "templateMessageId", "btnList", "responseType", "inlineKeyboardMarkup", "replyKeyboardMarkup", "replyKeyboardRemove")
    GENERALMESSAGE_FIELD_NUMBER: _ClassVar[int]
    TEMPLATEMESSAGEID_FIELD_NUMBER: _ClassVar[int]
    BTNLIST_FIELD_NUMBER: _ClassVar[int]
    RESPONSETYPE_FIELD_NUMBER: _ClassVar[int]
    INLINEKEYBOARDMARKUP_FIELD_NUMBER: _ClassVar[int]
    REPLYKEYBOARDMARKUP_FIELD_NUMBER: _ClassVar[int]
    REPLYKEYBOARDREMOVE_FIELD_NUMBER: _ClassVar[int]
    generalMessage: WebMessage
    templateMessageId: int
    btnList: _containers.RepeatedCompositeFieldContainer[WebBtnList]
    responseType: WebStringValue
    inlineKeyboardMarkup: WebInlineKeyboardMarkup
    replyKeyboardMarkup: WebReplyKeyboardMarkup
    replyKeyboardRemove: WebReplyKeyboardRemove
    def __init__(self, generalMessage: _Optional[_Union[WebMessage, _Mapping]] = ..., templateMessageId: _Optional[int] = ..., btnList: _Optional[_Iterable[_Union[WebBtnList, _Mapping]]] = ..., responseType: _Optional[_Union[WebStringValue, _Mapping]] = ..., inlineKeyboardMarkup: _Optional[_Union[WebInlineKeyboardMarkup, _Mapping]] = ..., replyKeyboardMarkup: _Optional[_Union[WebReplyKeyboardMarkup, _Mapping]] = ..., replyKeyboardRemove: _Optional[_Union[WebReplyKeyboardRemove, _Mapping]] = ...) -> None: ...

class WebTemplateMessageResponse(_message.Message):
    __slots__ = ("tmrMessage", "templateMessageResponseId", "message")
    TMRMESSAGE_FIELD_NUMBER: _ClassVar[int]
    TEMPLATEMESSAGERESPONSEID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    tmrMessage: str
    templateMessageResponseId: int
    message: WebMessage
    def __init__(self, tmrMessage: _Optional[str] = ..., templateMessageResponseId: _Optional[int] = ..., message: _Optional[_Union[WebMessage, _Mapping]] = ...) -> None: ...

class WebTerminationSignal(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebTextChunk(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class WebTextCommand(_message.Message):
    __slots__ = ("command", "args")
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    command: str
    args: str
    def __init__(self, command: _Optional[str] = ..., args: _Optional[str] = ...) -> None: ...

class WebTextExMarkdown(_message.Message):
    __slots__ = ("markdown",)
    MARKDOWN_FIELD_NUMBER: _ClassVar[int]
    markdown: str
    def __init__(self, markdown: _Optional[str] = ...) -> None: ...

class WebTextLinkPreview(_message.Message):
    __slots__ = ("linkPreview",)
    LINKPREVIEW_FIELD_NUMBER: _ClassVar[int]
    linkPreview: WebLinkPreview
    def __init__(self, linkPreview: _Optional[_Union[WebLinkPreview, _Mapping]] = ...) -> None: ...

class WebTextMessage(_message.Message):
    __slots__ = ("text", "mentions", "ext", "messageTag")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    MENTIONS_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    MESSAGETAG_FIELD_NUMBER: _ClassVar[int]
    text: str
    mentions: _containers.RepeatedScalarFieldContainer[int]
    ext: WebT_Z_95053
    messageTag: WebMessageTag
    def __init__(self, text: _Optional[str] = ..., mentions: _Optional[_Iterable[int]] = ..., ext: _Optional[_Union[WebT_Z_95053, _Mapping]] = ..., messageTag: _Optional[_Union[WebMessageTag, _Mapping]] = ...) -> None: ...

class WebTextModernMessage(_message.Message):
    __slots__ = ("text", "senderNameOverride", "senderPhotoOverride", "style", "attaches")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    SENDERNAMEOVERRIDE_FIELD_NUMBER: _ClassVar[int]
    SENDERPHOTOOVERRIDE_FIELD_NUMBER: _ClassVar[int]
    STYLE_FIELD_NUMBER: _ClassVar[int]
    ATTACHES_FIELD_NUMBER: _ClassVar[int]
    text: WebStringValue
    senderNameOverride: WebStringValue
    senderPhotoOverride: WebAvatar
    style: WebStyle
    attaches: _containers.RepeatedCompositeFieldContainer[WebAttache]
    def __init__(self, text: _Optional[_Union[WebStringValue, _Mapping]] = ..., senderNameOverride: _Optional[_Union[WebStringValue, _Mapping]] = ..., senderPhotoOverride: _Optional[_Union[WebAvatar, _Mapping]] = ..., style: _Optional[_Union[WebStyle, _Mapping]] = ..., attaches: _Optional[_Iterable[_Union[WebAttache, _Mapping]]] = ...) -> None: ...

class WebThreadDeleteMessage(_message.Message):
    __slots__ = ("peer", "rids", "dates", "threadIds", "quotedCommentReplySenderIds")
    PEER_FIELD_NUMBER: _ClassVar[int]
    RIDS_FIELD_NUMBER: _ClassVar[int]
    DATES_FIELD_NUMBER: _ClassVar[int]
    THREADIDS_FIELD_NUMBER: _ClassVar[int]
    QUOTEDCOMMENTREPLYSENDERIDS_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    rids: _containers.RepeatedScalarFieldContainer[int]
    dates: WebDates
    threadIds: _containers.RepeatedCompositeFieldContainer[WebMessageId]
    quotedCommentReplySenderIds: _containers.RepeatedCompositeFieldContainer[WebInt32Value_1]
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., rids: _Optional[_Iterable[int]] = ..., dates: _Optional[_Union[WebDates, _Mapping]] = ..., threadIds: _Optional[_Iterable[_Union[WebMessageId, _Mapping]]] = ..., quotedCommentReplySenderIds: _Optional[_Iterable[_Union[WebInt32Value_1, _Mapping]]] = ...) -> None: ...

class WebThreadEditMessage(_message.Message):
    __slots__ = ("peer", "rid", "message", "date", "updaterUserId", "threadId", "quotedCommentReplySenderId", "updatedContentTypeMessage", "exPeer")
    PEER_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    UPDATERUSERID_FIELD_NUMBER: _ClassVar[int]
    THREADID_FIELD_NUMBER: _ClassVar[int]
    QUOTEDCOMMENTREPLYSENDERID_FIELD_NUMBER: _ClassVar[int]
    UPDATEDCONTENTTYPEMESSAGE_FIELD_NUMBER: _ClassVar[int]
    EXPEER_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    rid: int
    message: WebMessage
    date: WebInt64Value_1
    updaterUserId: WebInt32Value
    threadId: WebMessageId
    quotedCommentReplySenderId: WebInt32Value_1
    updatedContentTypeMessage: WebMessage
    exPeer: WebExPeer
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., rid: _Optional[int] = ..., message: _Optional[_Union[WebMessage, _Mapping]] = ..., date: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., updaterUserId: _Optional[_Union[WebInt32Value, _Mapping]] = ..., threadId: _Optional[_Union[WebMessageId, _Mapping]] = ..., quotedCommentReplySenderId: _Optional[_Union[WebInt32Value_1, _Mapping]] = ..., updatedContentTypeMessage: _Optional[_Union[WebMessage, _Mapping]] = ..., exPeer: _Optional[_Union[WebExPeer, _Mapping]] = ...) -> None: ...

class WebThreadMessage(_message.Message):
    __slots__ = ("peer", "senderUid", "date", "rid", "message", "attributes", "quotedMessage", "previousMessageId", "groupedId", "isSilent", "hasComment", "threadId", "exPeer", "threadPreviousMessageId")
    PEER_FIELD_NUMBER: _ClassVar[int]
    SENDERUID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    QUOTEDMESSAGE_FIELD_NUMBER: _ClassVar[int]
    PREVIOUSMESSAGEID_FIELD_NUMBER: _ClassVar[int]
    GROUPEDID_FIELD_NUMBER: _ClassVar[int]
    ISSILENT_FIELD_NUMBER: _ClassVar[int]
    HASCOMMENT_FIELD_NUMBER: _ClassVar[int]
    THREADID_FIELD_NUMBER: _ClassVar[int]
    EXPEER_FIELD_NUMBER: _ClassVar[int]
    THREADPREVIOUSMESSAGEID_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    senderUid: int
    date: int
    rid: int
    message: WebMessage
    attributes: WebAttributes
    quotedMessage: WebQuotedMessage
    previousMessageId: WebMessageId
    groupedId: WebInt64Value_1
    isSilent: bool
    hasComment: bool
    threadId: WebMessageId
    exPeer: WebExPeer
    threadPreviousMessageId: WebMessageId
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., senderUid: _Optional[int] = ..., date: _Optional[int] = ..., rid: _Optional[int] = ..., message: _Optional[_Union[WebMessage, _Mapping]] = ..., attributes: _Optional[_Union[WebAttributes, _Mapping]] = ..., quotedMessage: _Optional[_Union[WebQuotedMessage, _Mapping]] = ..., previousMessageId: _Optional[_Union[WebMessageId, _Mapping]] = ..., groupedId: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., isSilent: _Optional[bool] = ..., hasComment: _Optional[bool] = ..., threadId: _Optional[_Union[WebMessageId, _Mapping]] = ..., exPeer: _Optional[_Union[WebExPeer, _Mapping]] = ..., threadPreviousMessageId: _Optional[_Union[WebMessageId, _Mapping]] = ...) -> None: ...

class WebThumb(_message.Message):
    __slots__ = ("w", "h", "thumb", "optFileLocation")
    W_FIELD_NUMBER: _ClassVar[int]
    H_FIELD_NUMBER: _ClassVar[int]
    THUMB_FIELD_NUMBER: _ClassVar[int]
    OPTFILELOCATION_FIELD_NUMBER: _ClassVar[int]
    w: int
    h: int
    thumb: bytes
    optFileLocation: WebFileLocation
    def __init__(self, w: _Optional[int] = ..., h: _Optional[int] = ..., thumb: _Optional[bytes] = ..., optFileLocation: _Optional[_Union[WebFileLocation, _Mapping]] = ...) -> None: ...

class WebTopicCreated(_message.Message):
    __slots__ = ("exPeer", "topicId", "title")
    EXPEER_FIELD_NUMBER: _ClassVar[int]
    TOPICID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    exPeer: WebExPeer
    topicId: WebMessageId
    title: str
    def __init__(self, exPeer: _Optional[_Union[WebExPeer, _Mapping]] = ..., topicId: _Optional[_Union[WebMessageId, _Mapping]] = ..., title: _Optional[str] = ...) -> None: ...

class WebTopicDeleted(_message.Message):
    __slots__ = ("exPeer", "topicId")
    EXPEER_FIELD_NUMBER: _ClassVar[int]
    TOPICID_FIELD_NUMBER: _ClassVar[int]
    exPeer: WebExPeer
    topicId: WebMessageId
    def __init__(self, exPeer: _Optional[_Union[WebExPeer, _Mapping]] = ..., topicId: _Optional[_Union[WebMessageId, _Mapping]] = ...) -> None: ...

class WebTopicEdited(_message.Message):
    __slots__ = ("exPeer", "topicId", "title")
    EXPEER_FIELD_NUMBER: _ClassVar[int]
    TOPICID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    exPeer: WebExPeer
    topicId: WebMessageId
    title: str
    def __init__(self, exPeer: _Optional[_Union[WebExPeer, _Mapping]] = ..., topicId: _Optional[_Union[WebMessageId, _Mapping]] = ..., title: _Optional[str] = ...) -> None: ...

class WebTranscriptReady(_message.Message):
    __slots__ = ("downloadSource", "outPeer", "messageId", "error")
    DOWNLOADSOURCE_FIELD_NUMBER: _ClassVar[int]
    OUTPEER_FIELD_NUMBER: _ClassVar[int]
    MESSAGEID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    downloadSource: WebDownloadSource
    outPeer: WebOutPeer
    messageId: WebMessageId
    error: WebError
    def __init__(self, downloadSource: _Optional[_Union[WebDownloadSource, _Mapping]] = ..., outPeer: _Optional[_Union[WebOutPeer, _Mapping]] = ..., messageId: _Optional[_Union[WebMessageId, _Mapping]] = ..., error: _Optional[_Union[WebError, _Mapping]] = ...) -> None: ...

class WebType(_message.Message):
    __slots__ = ("openDialogAction", "openUrlAction", "showSnackBarAction", "doNothingAction")
    OPENDIALOGACTION_FIELD_NUMBER: _ClassVar[int]
    OPENURLACTION_FIELD_NUMBER: _ClassVar[int]
    SHOWSNACKBARACTION_FIELD_NUMBER: _ClassVar[int]
    DONOTHINGACTION_FIELD_NUMBER: _ClassVar[int]
    openDialogAction: WebT_iG_95053
    openUrlAction: WebOpenUrlAction
    showSnackBarAction: WebShowSnackBarAction
    doNothingAction: WebDoNothingAction
    def __init__(self, openDialogAction: _Optional[_Union[WebT_iG_95053, _Mapping]] = ..., openUrlAction: _Optional[_Union[WebOpenUrlAction, _Mapping]] = ..., showSnackBarAction: _Optional[_Union[WebShowSnackBarAction, _Mapping]] = ..., doNothingAction: _Optional[_Union[WebDoNothingAction, _Mapping]] = ...) -> None: ...

class WebTyping(_message.Message):
    __slots__ = ("peer", "uid", "typingType")
    PEER_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    TYPINGTYPE_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    uid: int
    typingType: int
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., uid: _Optional[int] = ..., typingType: _Optional[int] = ...) -> None: ...

class WebTypingStop(_message.Message):
    __slots__ = ("peer", "uid", "typingType")
    PEER_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    TYPINGTYPE_FIELD_NUMBER: _ClassVar[int]
    peer: WebBot
    uid: int
    typingType: int
    def __init__(self, peer: _Optional[_Union[WebBot, _Mapping]] = ..., uid: _Optional[int] = ..., typingType: _Optional[int] = ...) -> None: ...

class WebUnsignedUrlHeader(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class WebUnsupportedMessage(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebUpdate(_message.Message):
    __slots__ = ("chatGroupsChanged", "messageSent", "contactRegistered", "typing", "userOnline", "userOffline", "userLastSeen", "userAvatarChanged", "messageRead", "groupUserInvitedObsolete", "groupUserLeaveObsolete", "groupUserKickObsolete", "userNameChanged", "groupOnline", "userLastSeenUnknown", "groupInviteObsolete", "groupTitleChangedObsolete", "groupAvatarChangedObsolete", "contactsAdded", "contactsRemoved", "groupMembersUpdateObsolete", "messageDelete", "chatClear", "chatDelete", "messageReadByMe", "userLocalNameChanged", "messageReceived", "message", "groupNicknameChanged", "rawUpdate", "typingStop", "emptyUpdate", "forceClearCache", "chatShow", "chatArchive", "chatFavourite", "parameterChanged", "userContactsChanged", "ownStickersChanged", "messageContentChanged", "messageDateChanged", "stickerCollectionsChanged", "messageQuotedChanged", "userNickChanged", "userAboutChanged", "userPreferredLanguagesChanged", "groupTopicChangedObsolete", "groupAboutChangedObsolete", "userTimeZoneChanged", "userBotCommandsChanged", "userExtChanged", "userFullExtChanged", "reactionsUpdate", "userExInfoChanged", "userDefaultBankAccountChanged", "userDefaultCardNumberChanged", "userDefaultCardNumberRemoved", "cardinalityChanged", "groupMessagePinned", "groupPinRemoved", "groupRestrictionChanged", "groupTitleChanged", "groupAvatarChanged", "groupMemberChanged", "groupExtChanged", "groupMembersUpdated", "groupMembersBecameAsync", "groupTopicChanged", "groupAboutChanged", "groupFullExtChanged", "groupOwnerChanged", "groupHistoryShared", "groupMembersCountChanged", "groupMemberDiff", "groupCanSendMessagesChanged", "groupCanViewMembersChanged", "groupCanInviteMembersChanged", "groupMemberAdminChanged", "groupBecameOrphaned", "userBlocked", "userUnblocked", "groupExInfoChanged", "channelNickChanged", "requestLogin", "accountDeleted", "channelAdvertisementTypeChanged", "channelAdTagIdChanged", "phoneNumberChanged", "groupMemberPermissionsChanged", "groupDefaultPermissionsChanged", "vitrineChanged", "callStarted", "callAccepted", "callDiscarded", "callReceived", "groupCallStarted", "groupCallEnded", "callReactionSent", "stickerPacksChanged", "messages", "callUpgraded", "peersInvited", "multiPeerCallStarted", "peersStateChanged", "savedGifsChanged", "hidePrivacyBar", "messageReactions", "callLinkGenerated", "callJoinRequestReceived", "callJoinRequestAnswered", "mentionReadByMe", "pinnedDialogsChanged", "messageReactionsReadByMe", "messageNewReaction", "callEvent", "startLive", "endLive", "folderCreated", "folderDeleted", "foldersReordered", "dialogsMarkedAsRead", "dialogsMarkedAsUnread", "folderEdited", "callAction", "dialogsUnpinned", "messagePinned", "messagesUnPinned", "transcriptReady", "generalNotificationMessage", "askBotReview", "dialogArchiveStatus", "premiumPurchaseStatus", "endpointChanged", "topicCreated", "topicEdited", "topicDeleted", "messageStreamChunks", "peerHaveScheduleTask", "allContactsRemoved", "requestBankiAccessFor", "walletUpdated", "walletBalanceUpdated")
    CHATGROUPSCHANGED_FIELD_NUMBER: _ClassVar[int]
    MESSAGESENT_FIELD_NUMBER: _ClassVar[int]
    CONTACTREGISTERED_FIELD_NUMBER: _ClassVar[int]
    TYPING_FIELD_NUMBER: _ClassVar[int]
    USERONLINE_FIELD_NUMBER: _ClassVar[int]
    USEROFFLINE_FIELD_NUMBER: _ClassVar[int]
    USERLASTSEEN_FIELD_NUMBER: _ClassVar[int]
    USERAVATARCHANGED_FIELD_NUMBER: _ClassVar[int]
    MESSAGEREAD_FIELD_NUMBER: _ClassVar[int]
    GROUPUSERINVITEDOBSOLETE_FIELD_NUMBER: _ClassVar[int]
    GROUPUSERLEAVEOBSOLETE_FIELD_NUMBER: _ClassVar[int]
    GROUPUSERKICKOBSOLETE_FIELD_NUMBER: _ClassVar[int]
    USERNAMECHANGED_FIELD_NUMBER: _ClassVar[int]
    GROUPONLINE_FIELD_NUMBER: _ClassVar[int]
    USERLASTSEENUNKNOWN_FIELD_NUMBER: _ClassVar[int]
    GROUPINVITEOBSOLETE_FIELD_NUMBER: _ClassVar[int]
    GROUPTITLECHANGEDOBSOLETE_FIELD_NUMBER: _ClassVar[int]
    GROUPAVATARCHANGEDOBSOLETE_FIELD_NUMBER: _ClassVar[int]
    CONTACTSADDED_FIELD_NUMBER: _ClassVar[int]
    CONTACTSREMOVED_FIELD_NUMBER: _ClassVar[int]
    GROUPMEMBERSUPDATEOBSOLETE_FIELD_NUMBER: _ClassVar[int]
    MESSAGEDELETE_FIELD_NUMBER: _ClassVar[int]
    CHATCLEAR_FIELD_NUMBER: _ClassVar[int]
    CHATDELETE_FIELD_NUMBER: _ClassVar[int]
    MESSAGEREADBYME_FIELD_NUMBER: _ClassVar[int]
    USERLOCALNAMECHANGED_FIELD_NUMBER: _ClassVar[int]
    MESSAGERECEIVED_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    GROUPNICKNAMECHANGED_FIELD_NUMBER: _ClassVar[int]
    RAWUPDATE_FIELD_NUMBER: _ClassVar[int]
    TYPINGSTOP_FIELD_NUMBER: _ClassVar[int]
    EMPTYUPDATE_FIELD_NUMBER: _ClassVar[int]
    FORCECLEARCACHE_FIELD_NUMBER: _ClassVar[int]
    CHATSHOW_FIELD_NUMBER: _ClassVar[int]
    CHATARCHIVE_FIELD_NUMBER: _ClassVar[int]
    CHATFAVOURITE_FIELD_NUMBER: _ClassVar[int]
    PARAMETERCHANGED_FIELD_NUMBER: _ClassVar[int]
    USERCONTACTSCHANGED_FIELD_NUMBER: _ClassVar[int]
    OWNSTICKERSCHANGED_FIELD_NUMBER: _ClassVar[int]
    MESSAGECONTENTCHANGED_FIELD_NUMBER: _ClassVar[int]
    MESSAGEDATECHANGED_FIELD_NUMBER: _ClassVar[int]
    STICKERCOLLECTIONSCHANGED_FIELD_NUMBER: _ClassVar[int]
    MESSAGEQUOTEDCHANGED_FIELD_NUMBER: _ClassVar[int]
    USERNICKCHANGED_FIELD_NUMBER: _ClassVar[int]
    USERABOUTCHANGED_FIELD_NUMBER: _ClassVar[int]
    USERPREFERREDLANGUAGESCHANGED_FIELD_NUMBER: _ClassVar[int]
    GROUPTOPICCHANGEDOBSOLETE_FIELD_NUMBER: _ClassVar[int]
    GROUPABOUTCHANGEDOBSOLETE_FIELD_NUMBER: _ClassVar[int]
    USERTIMEZONECHANGED_FIELD_NUMBER: _ClassVar[int]
    USERBOTCOMMANDSCHANGED_FIELD_NUMBER: _ClassVar[int]
    USEREXTCHANGED_FIELD_NUMBER: _ClassVar[int]
    USERFULLEXTCHANGED_FIELD_NUMBER: _ClassVar[int]
    REACTIONSUPDATE_FIELD_NUMBER: _ClassVar[int]
    USEREXINFOCHANGED_FIELD_NUMBER: _ClassVar[int]
    USERDEFAULTBANKACCOUNTCHANGED_FIELD_NUMBER: _ClassVar[int]
    USERDEFAULTCARDNUMBERCHANGED_FIELD_NUMBER: _ClassVar[int]
    USERDEFAULTCARDNUMBERREMOVED_FIELD_NUMBER: _ClassVar[int]
    CARDINALITYCHANGED_FIELD_NUMBER: _ClassVar[int]
    GROUPMESSAGEPINNED_FIELD_NUMBER: _ClassVar[int]
    GROUPPINREMOVED_FIELD_NUMBER: _ClassVar[int]
    GROUPRESTRICTIONCHANGED_FIELD_NUMBER: _ClassVar[int]
    GROUPTITLECHANGED_FIELD_NUMBER: _ClassVar[int]
    GROUPAVATARCHANGED_FIELD_NUMBER: _ClassVar[int]
    GROUPMEMBERCHANGED_FIELD_NUMBER: _ClassVar[int]
    GROUPEXTCHANGED_FIELD_NUMBER: _ClassVar[int]
    GROUPMEMBERSUPDATED_FIELD_NUMBER: _ClassVar[int]
    GROUPMEMBERSBECAMEASYNC_FIELD_NUMBER: _ClassVar[int]
    GROUPTOPICCHANGED_FIELD_NUMBER: _ClassVar[int]
    GROUPABOUTCHANGED_FIELD_NUMBER: _ClassVar[int]
    GROUPFULLEXTCHANGED_FIELD_NUMBER: _ClassVar[int]
    GROUPOWNERCHANGED_FIELD_NUMBER: _ClassVar[int]
    GROUPHISTORYSHARED_FIELD_NUMBER: _ClassVar[int]
    GROUPMEMBERSCOUNTCHANGED_FIELD_NUMBER: _ClassVar[int]
    GROUPMEMBERDIFF_FIELD_NUMBER: _ClassVar[int]
    GROUPCANSENDMESSAGESCHANGED_FIELD_NUMBER: _ClassVar[int]
    GROUPCANVIEWMEMBERSCHANGED_FIELD_NUMBER: _ClassVar[int]
    GROUPCANINVITEMEMBERSCHANGED_FIELD_NUMBER: _ClassVar[int]
    GROUPMEMBERADMINCHANGED_FIELD_NUMBER: _ClassVar[int]
    GROUPBECAMEORPHANED_FIELD_NUMBER: _ClassVar[int]
    USERBLOCKED_FIELD_NUMBER: _ClassVar[int]
    USERUNBLOCKED_FIELD_NUMBER: _ClassVar[int]
    GROUPEXINFOCHANGED_FIELD_NUMBER: _ClassVar[int]
    CHANNELNICKCHANGED_FIELD_NUMBER: _ClassVar[int]
    REQUESTLOGIN_FIELD_NUMBER: _ClassVar[int]
    ACCOUNTDELETED_FIELD_NUMBER: _ClassVar[int]
    CHANNELADVERTISEMENTTYPECHANGED_FIELD_NUMBER: _ClassVar[int]
    CHANNELADTAGIDCHANGED_FIELD_NUMBER: _ClassVar[int]
    PHONENUMBERCHANGED_FIELD_NUMBER: _ClassVar[int]
    GROUPMEMBERPERMISSIONSCHANGED_FIELD_NUMBER: _ClassVar[int]
    GROUPDEFAULTPERMISSIONSCHANGED_FIELD_NUMBER: _ClassVar[int]
    VITRINECHANGED_FIELD_NUMBER: _ClassVar[int]
    CALLSTARTED_FIELD_NUMBER: _ClassVar[int]
    CALLACCEPTED_FIELD_NUMBER: _ClassVar[int]
    CALLDISCARDED_FIELD_NUMBER: _ClassVar[int]
    CALLRECEIVED_FIELD_NUMBER: _ClassVar[int]
    GROUPCALLSTARTED_FIELD_NUMBER: _ClassVar[int]
    GROUPCALLENDED_FIELD_NUMBER: _ClassVar[int]
    CALLREACTIONSENT_FIELD_NUMBER: _ClassVar[int]
    STICKERPACKSCHANGED_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    CALLUPGRADED_FIELD_NUMBER: _ClassVar[int]
    PEERSINVITED_FIELD_NUMBER: _ClassVar[int]
    MULTIPEERCALLSTARTED_FIELD_NUMBER: _ClassVar[int]
    PEERSSTATECHANGED_FIELD_NUMBER: _ClassVar[int]
    SAVEDGIFSCHANGED_FIELD_NUMBER: _ClassVar[int]
    HIDEPRIVACYBAR_FIELD_NUMBER: _ClassVar[int]
    MESSAGEREACTIONS_FIELD_NUMBER: _ClassVar[int]
    CALLLINKGENERATED_FIELD_NUMBER: _ClassVar[int]
    CALLJOINREQUESTRECEIVED_FIELD_NUMBER: _ClassVar[int]
    CALLJOINREQUESTANSWERED_FIELD_NUMBER: _ClassVar[int]
    MENTIONREADBYME_FIELD_NUMBER: _ClassVar[int]
    PINNEDDIALOGSCHANGED_FIELD_NUMBER: _ClassVar[int]
    MESSAGEREACTIONSREADBYME_FIELD_NUMBER: _ClassVar[int]
    MESSAGENEWREACTION_FIELD_NUMBER: _ClassVar[int]
    CALLEVENT_FIELD_NUMBER: _ClassVar[int]
    STARTLIVE_FIELD_NUMBER: _ClassVar[int]
    ENDLIVE_FIELD_NUMBER: _ClassVar[int]
    FOLDERCREATED_FIELD_NUMBER: _ClassVar[int]
    FOLDERDELETED_FIELD_NUMBER: _ClassVar[int]
    FOLDERSREORDERED_FIELD_NUMBER: _ClassVar[int]
    DIALOGSMARKEDASREAD_FIELD_NUMBER: _ClassVar[int]
    DIALOGSMARKEDASUNREAD_FIELD_NUMBER: _ClassVar[int]
    FOLDEREDITED_FIELD_NUMBER: _ClassVar[int]
    CALLACTION_FIELD_NUMBER: _ClassVar[int]
    DIALOGSUNPINNED_FIELD_NUMBER: _ClassVar[int]
    MESSAGEPINNED_FIELD_NUMBER: _ClassVar[int]
    MESSAGESUNPINNED_FIELD_NUMBER: _ClassVar[int]
    TRANSCRIPTREADY_FIELD_NUMBER: _ClassVar[int]
    GENERALNOTIFICATIONMESSAGE_FIELD_NUMBER: _ClassVar[int]
    ASKBOTREVIEW_FIELD_NUMBER: _ClassVar[int]
    DIALOGARCHIVESTATUS_FIELD_NUMBER: _ClassVar[int]
    PREMIUMPURCHASESTATUS_FIELD_NUMBER: _ClassVar[int]
    ENDPOINTCHANGED_FIELD_NUMBER: _ClassVar[int]
    TOPICCREATED_FIELD_NUMBER: _ClassVar[int]
    TOPICEDITED_FIELD_NUMBER: _ClassVar[int]
    TOPICDELETED_FIELD_NUMBER: _ClassVar[int]
    MESSAGESTREAMCHUNKS_FIELD_NUMBER: _ClassVar[int]
    PEERHAVESCHEDULETASK_FIELD_NUMBER: _ClassVar[int]
    ALLCONTACTSREMOVED_FIELD_NUMBER: _ClassVar[int]
    REQUESTBANKIACCESSFOR_FIELD_NUMBER: _ClassVar[int]
    WALLETUPDATED_FIELD_NUMBER: _ClassVar[int]
    WALLETBALANCEUPDATED_FIELD_NUMBER: _ClassVar[int]
    chatGroupsChanged: WebChatGroupsChanged
    messageSent: WebMessageSent
    contactRegistered: WebContactRegistered
    typing: WebTyping
    userOnline: WebUserOnline
    userOffline: WebUserOffline
    userLastSeen: WebUserLastSeen
    userAvatarChanged: WebUserAvatarChanged
    messageRead: WebMessageRead
    groupUserInvitedObsolete: WebGroupUserInvitedObsolete
    groupUserLeaveObsolete: WebGroupUserLeaveObsolete
    groupUserKickObsolete: WebGroupUserKickObsolete
    userNameChanged: WebUserNameChanged
    groupOnline: WebGroupOnline
    userLastSeenUnknown: WebUserLastSeenUnknown
    groupInviteObsolete: WebGroupInviteObsolete
    groupTitleChangedObsolete: WebGroupTitleChangedObsolete
    groupAvatarChangedObsolete: WebGroupAvatarChangedObsolete
    contactsAdded: WebContactsAdded
    contactsRemoved: WebContactsRemoved
    groupMembersUpdateObsolete: WebGroupMembersUpdateObsolete
    messageDelete: WebThreadDeleteMessage
    chatClear: WebChatClear
    chatDelete: WebChatDelete
    messageReadByMe: WebMessageReadByMe
    userLocalNameChanged: WebUserLocalNameChanged
    messageReceived: WebMessageReceived
    message: WebThreadMessage
    groupNicknameChanged: WebGroupNicknameChanged
    rawUpdate: WebRawUpdate
    typingStop: WebTypingStop
    emptyUpdate: WebEmptyUpdate
    forceClearCache: WebForceClearCache
    chatShow: WebChatShow
    chatArchive: WebChatArchive
    chatFavourite: WebChatFavourite
    parameterChanged: WebParameterChanged
    userContactsChanged: WebUserContactsChanged
    ownStickersChanged: WebOwnStickersChanged
    messageContentChanged: WebThreadEditMessage
    messageDateChanged: WebMessageDateChanged
    stickerCollectionsChanged: WebStickerCollectionsChanged
    messageQuotedChanged: WebMessageQuotedChanged
    userNickChanged: WebUserNickChanged
    userAboutChanged: WebUserAboutChanged
    userPreferredLanguagesChanged: WebUserPreferredLanguagesChanged
    groupTopicChangedObsolete: WebGroupTopicChangedObsolete
    groupAboutChangedObsolete: WebGroupAboutChangedObsolete
    userTimeZoneChanged: WebUserTimeZoneChanged
    userBotCommandsChanged: WebUserBotCommandsChanged
    userExtChanged: WebUserExtChanged
    userFullExtChanged: WebUserFullExtChanged
    reactionsUpdate: WebReactionsUpdate
    userExInfoChanged: WebUserExInfoChanged
    userDefaultBankAccountChanged: WebUserDefaultBankAccountChanged
    userDefaultCardNumberChanged: WebUserDefaultCardNumberChanged
    userDefaultCardNumberRemoved: WebUserDefaultCardNumberRemoved
    cardinalityChanged: WebCardinalityChanged
    groupMessagePinned: WebGroupMessagePinned
    groupPinRemoved: WebGroupPinRemoved
    groupRestrictionChanged: WebGroupRestrictionChanged
    groupTitleChanged: WebGroupTitleChanged
    groupAvatarChanged: WebGroupAvatarChanged
    groupMemberChanged: WebGroupMemberChanged
    groupExtChanged: WebGroupExtChanged
    groupMembersUpdated: WebGroupMembersUpdated
    groupMembersBecameAsync: WebGroupMembersBecameAsync
    groupTopicChanged: WebGroupTopicChanged
    groupAboutChanged: WebGroupAboutChanged
    groupFullExtChanged: WebGroupFullExtChanged
    groupOwnerChanged: WebGroupOwnerChanged
    groupHistoryShared: WebGroupHistoryShared
    groupMembersCountChanged: WebGroupMembersCountChanged
    groupMemberDiff: WebGroupMemberDiff
    groupCanSendMessagesChanged: WebGroupCanSendMessagesChanged
    groupCanViewMembersChanged: WebGroupCanViewMembersChanged
    groupCanInviteMembersChanged: WebGroupCanInviteMembersChanged
    groupMemberAdminChanged: WebGroupMemberAdminChanged
    groupBecameOrphaned: WebGroupBecameOrphaned
    userBlocked: WebUserBlocked
    userUnblocked: WebUserUnblocked
    groupExInfoChanged: WebGroupExInfoChanged
    channelNickChanged: WebChannelNickChanged
    requestLogin: WebRequestLogin
    accountDeleted: WebAccountDeleted
    channelAdvertisementTypeChanged: WebChannelAdvertisementTypeChanged
    channelAdTagIdChanged: WebChannelAdTagIdChanged
    phoneNumberChanged: WebPhoneNumberChanged
    groupMemberPermissionsChanged: WebGroupMemberPermissionsChanged
    groupDefaultPermissionsChanged: WebGroupDefaultPermissionsChanged
    vitrineChanged: WebVitrineChanged
    callStarted: WebCallStarted
    callAccepted: WebCallAccepted
    callDiscarded: WebCallDiscarded
    callReceived: WebCallReceived
    groupCallStarted: WebGroupCallStarted
    groupCallEnded: WebGroupCallEnded
    callReactionSent: WebCallReactionSent
    stickerPacksChanged: WebStickerPacksChanged
    messages: WebMessages
    callUpgraded: WebCallUpgraded
    peersInvited: WebPeersInvited
    multiPeerCallStarted: WebMultiPeerCallStarted
    peersStateChanged: WebPeersStateChanged
    savedGifsChanged: WebSavedGifsChanged
    hidePrivacyBar: WebHidePrivacyBar
    messageReactions: WebMessageReaction
    callLinkGenerated: WebCallLinkGenerated
    callJoinRequestReceived: WebCallJoinRequestReceived
    callJoinRequestAnswered: WebCallJoinRequestAnswered
    mentionReadByMe: WebMentionReadByMe
    pinnedDialogsChanged: WebPinnedDialogsChanged
    messageReactionsReadByMe: WebMessageReactionsReadByMe
    messageNewReaction: WebMessageNewReaction
    callEvent: WebCallEvent
    startLive: WebStartLive
    endLive: WebEndLive
    folderCreated: WebFolderCreated
    folderDeleted: WebFolderDeleted
    foldersReordered: WebFoldersReordered
    dialogsMarkedAsRead: WebDialogsMarkedAsRead
    dialogsMarkedAsUnread: WebDialogsMarkedAsUnread
    folderEdited: WebFolderEdited
    callAction: WebCallAction
    dialogsUnpinned: WebDialogsUnpinned
    messagePinned: WebMessagePinned
    messagesUnPinned: WebMessagesUnPinned
    transcriptReady: WebTranscriptReady
    generalNotificationMessage: WebGeneralNotificationMessage
    askBotReview: WebAskBotReview
    dialogArchiveStatus: WebDialogArchiveStatus
    premiumPurchaseStatus: WebPremiumPurchaseStatus
    endpointChanged: WebEndpointChanged
    topicCreated: WebTopicCreated
    topicEdited: WebTopicEdited
    topicDeleted: WebTopicDeleted
    messageStreamChunks: WebMessageStreamChunks
    peerHaveScheduleTask: WebPeerHaveScheduleTask
    allContactsRemoved: WebAllContactsRemoved
    requestBankiAccessFor: WebRequestBankiAccessFor
    walletUpdated: WebWalletUpdated
    walletBalanceUpdated: WebWalletBalanceUpdated
    def __init__(self, chatGroupsChanged: _Optional[_Union[WebChatGroupsChanged, _Mapping]] = ..., messageSent: _Optional[_Union[WebMessageSent, _Mapping]] = ..., contactRegistered: _Optional[_Union[WebContactRegistered, _Mapping]] = ..., typing: _Optional[_Union[WebTyping, _Mapping]] = ..., userOnline: _Optional[_Union[WebUserOnline, _Mapping]] = ..., userOffline: _Optional[_Union[WebUserOffline, _Mapping]] = ..., userLastSeen: _Optional[_Union[WebUserLastSeen, _Mapping]] = ..., userAvatarChanged: _Optional[_Union[WebUserAvatarChanged, _Mapping]] = ..., messageRead: _Optional[_Union[WebMessageRead, _Mapping]] = ..., groupUserInvitedObsolete: _Optional[_Union[WebGroupUserInvitedObsolete, _Mapping]] = ..., groupUserLeaveObsolete: _Optional[_Union[WebGroupUserLeaveObsolete, _Mapping]] = ..., groupUserKickObsolete: _Optional[_Union[WebGroupUserKickObsolete, _Mapping]] = ..., userNameChanged: _Optional[_Union[WebUserNameChanged, _Mapping]] = ..., groupOnline: _Optional[_Union[WebGroupOnline, _Mapping]] = ..., userLastSeenUnknown: _Optional[_Union[WebUserLastSeenUnknown, _Mapping]] = ..., groupInviteObsolete: _Optional[_Union[WebGroupInviteObsolete, _Mapping]] = ..., groupTitleChangedObsolete: _Optional[_Union[WebGroupTitleChangedObsolete, _Mapping]] = ..., groupAvatarChangedObsolete: _Optional[_Union[WebGroupAvatarChangedObsolete, _Mapping]] = ..., contactsAdded: _Optional[_Union[WebContactsAdded, _Mapping]] = ..., contactsRemoved: _Optional[_Union[WebContactsRemoved, _Mapping]] = ..., groupMembersUpdateObsolete: _Optional[_Union[WebGroupMembersUpdateObsolete, _Mapping]] = ..., messageDelete: _Optional[_Union[WebThreadDeleteMessage, _Mapping]] = ..., chatClear: _Optional[_Union[WebChatClear, _Mapping]] = ..., chatDelete: _Optional[_Union[WebChatDelete, _Mapping]] = ..., messageReadByMe: _Optional[_Union[WebMessageReadByMe, _Mapping]] = ..., userLocalNameChanged: _Optional[_Union[WebUserLocalNameChanged, _Mapping]] = ..., messageReceived: _Optional[_Union[WebMessageReceived, _Mapping]] = ..., message: _Optional[_Union[WebThreadMessage, _Mapping]] = ..., groupNicknameChanged: _Optional[_Union[WebGroupNicknameChanged, _Mapping]] = ..., rawUpdate: _Optional[_Union[WebRawUpdate, _Mapping]] = ..., typingStop: _Optional[_Union[WebTypingStop, _Mapping]] = ..., emptyUpdate: _Optional[_Union[WebEmptyUpdate, _Mapping]] = ..., forceClearCache: _Optional[_Union[WebForceClearCache, _Mapping]] = ..., chatShow: _Optional[_Union[WebChatShow, _Mapping]] = ..., chatArchive: _Optional[_Union[WebChatArchive, _Mapping]] = ..., chatFavourite: _Optional[_Union[WebChatFavourite, _Mapping]] = ..., parameterChanged: _Optional[_Union[WebParameterChanged, _Mapping]] = ..., userContactsChanged: _Optional[_Union[WebUserContactsChanged, _Mapping]] = ..., ownStickersChanged: _Optional[_Union[WebOwnStickersChanged, _Mapping]] = ..., messageContentChanged: _Optional[_Union[WebThreadEditMessage, _Mapping]] = ..., messageDateChanged: _Optional[_Union[WebMessageDateChanged, _Mapping]] = ..., stickerCollectionsChanged: _Optional[_Union[WebStickerCollectionsChanged, _Mapping]] = ..., messageQuotedChanged: _Optional[_Union[WebMessageQuotedChanged, _Mapping]] = ..., userNickChanged: _Optional[_Union[WebUserNickChanged, _Mapping]] = ..., userAboutChanged: _Optional[_Union[WebUserAboutChanged, _Mapping]] = ..., userPreferredLanguagesChanged: _Optional[_Union[WebUserPreferredLanguagesChanged, _Mapping]] = ..., groupTopicChangedObsolete: _Optional[_Union[WebGroupTopicChangedObsolete, _Mapping]] = ..., groupAboutChangedObsolete: _Optional[_Union[WebGroupAboutChangedObsolete, _Mapping]] = ..., userTimeZoneChanged: _Optional[_Union[WebUserTimeZoneChanged, _Mapping]] = ..., userBotCommandsChanged: _Optional[_Union[WebUserBotCommandsChanged, _Mapping]] = ..., userExtChanged: _Optional[_Union[WebUserExtChanged, _Mapping]] = ..., userFullExtChanged: _Optional[_Union[WebUserFullExtChanged, _Mapping]] = ..., reactionsUpdate: _Optional[_Union[WebReactionsUpdate, _Mapping]] = ..., userExInfoChanged: _Optional[_Union[WebUserExInfoChanged, _Mapping]] = ..., userDefaultBankAccountChanged: _Optional[_Union[WebUserDefaultBankAccountChanged, _Mapping]] = ..., userDefaultCardNumberChanged: _Optional[_Union[WebUserDefaultCardNumberChanged, _Mapping]] = ..., userDefaultCardNumberRemoved: _Optional[_Union[WebUserDefaultCardNumberRemoved, _Mapping]] = ..., cardinalityChanged: _Optional[_Union[WebCardinalityChanged, _Mapping]] = ..., groupMessagePinned: _Optional[_Union[WebGroupMessagePinned, _Mapping]] = ..., groupPinRemoved: _Optional[_Union[WebGroupPinRemoved, _Mapping]] = ..., groupRestrictionChanged: _Optional[_Union[WebGroupRestrictionChanged, _Mapping]] = ..., groupTitleChanged: _Optional[_Union[WebGroupTitleChanged, _Mapping]] = ..., groupAvatarChanged: _Optional[_Union[WebGroupAvatarChanged, _Mapping]] = ..., groupMemberChanged: _Optional[_Union[WebGroupMemberChanged, _Mapping]] = ..., groupExtChanged: _Optional[_Union[WebGroupExtChanged, _Mapping]] = ..., groupMembersUpdated: _Optional[_Union[WebGroupMembersUpdated, _Mapping]] = ..., groupMembersBecameAsync: _Optional[_Union[WebGroupMembersBecameAsync, _Mapping]] = ..., groupTopicChanged: _Optional[_Union[WebGroupTopicChanged, _Mapping]] = ..., groupAboutChanged: _Optional[_Union[WebGroupAboutChanged, _Mapping]] = ..., groupFullExtChanged: _Optional[_Union[WebGroupFullExtChanged, _Mapping]] = ..., groupOwnerChanged: _Optional[_Union[WebGroupOwnerChanged, _Mapping]] = ..., groupHistoryShared: _Optional[_Union[WebGroupHistoryShared, _Mapping]] = ..., groupMembersCountChanged: _Optional[_Union[WebGroupMembersCountChanged, _Mapping]] = ..., groupMemberDiff: _Optional[_Union[WebGroupMemberDiff, _Mapping]] = ..., groupCanSendMessagesChanged: _Optional[_Union[WebGroupCanSendMessagesChanged, _Mapping]] = ..., groupCanViewMembersChanged: _Optional[_Union[WebGroupCanViewMembersChanged, _Mapping]] = ..., groupCanInviteMembersChanged: _Optional[_Union[WebGroupCanInviteMembersChanged, _Mapping]] = ..., groupMemberAdminChanged: _Optional[_Union[WebGroupMemberAdminChanged, _Mapping]] = ..., groupBecameOrphaned: _Optional[_Union[WebGroupBecameOrphaned, _Mapping]] = ..., userBlocked: _Optional[_Union[WebUserBlocked, _Mapping]] = ..., userUnblocked: _Optional[_Union[WebUserUnblocked, _Mapping]] = ..., groupExInfoChanged: _Optional[_Union[WebGroupExInfoChanged, _Mapping]] = ..., channelNickChanged: _Optional[_Union[WebChannelNickChanged, _Mapping]] = ..., requestLogin: _Optional[_Union[WebRequestLogin, _Mapping]] = ..., accountDeleted: _Optional[_Union[WebAccountDeleted, _Mapping]] = ..., channelAdvertisementTypeChanged: _Optional[_Union[WebChannelAdvertisementTypeChanged, _Mapping]] = ..., channelAdTagIdChanged: _Optional[_Union[WebChannelAdTagIdChanged, _Mapping]] = ..., phoneNumberChanged: _Optional[_Union[WebPhoneNumberChanged, _Mapping]] = ..., groupMemberPermissionsChanged: _Optional[_Union[WebGroupMemberPermissionsChanged, _Mapping]] = ..., groupDefaultPermissionsChanged: _Optional[_Union[WebGroupDefaultPermissionsChanged, _Mapping]] = ..., vitrineChanged: _Optional[_Union[WebVitrineChanged, _Mapping]] = ..., callStarted: _Optional[_Union[WebCallStarted, _Mapping]] = ..., callAccepted: _Optional[_Union[WebCallAccepted, _Mapping]] = ..., callDiscarded: _Optional[_Union[WebCallDiscarded, _Mapping]] = ..., callReceived: _Optional[_Union[WebCallReceived, _Mapping]] = ..., groupCallStarted: _Optional[_Union[WebGroupCallStarted, _Mapping]] = ..., groupCallEnded: _Optional[_Union[WebGroupCallEnded, _Mapping]] = ..., callReactionSent: _Optional[_Union[WebCallReactionSent, _Mapping]] = ..., stickerPacksChanged: _Optional[_Union[WebStickerPacksChanged, _Mapping]] = ..., messages: _Optional[_Union[WebMessages, _Mapping]] = ..., callUpgraded: _Optional[_Union[WebCallUpgraded, _Mapping]] = ..., peersInvited: _Optional[_Union[WebPeersInvited, _Mapping]] = ..., multiPeerCallStarted: _Optional[_Union[WebMultiPeerCallStarted, _Mapping]] = ..., peersStateChanged: _Optional[_Union[WebPeersStateChanged, _Mapping]] = ..., savedGifsChanged: _Optional[_Union[WebSavedGifsChanged, _Mapping]] = ..., hidePrivacyBar: _Optional[_Union[WebHidePrivacyBar, _Mapping]] = ..., messageReactions: _Optional[_Union[WebMessageReaction, _Mapping]] = ..., callLinkGenerated: _Optional[_Union[WebCallLinkGenerated, _Mapping]] = ..., callJoinRequestReceived: _Optional[_Union[WebCallJoinRequestReceived, _Mapping]] = ..., callJoinRequestAnswered: _Optional[_Union[WebCallJoinRequestAnswered, _Mapping]] = ..., mentionReadByMe: _Optional[_Union[WebMentionReadByMe, _Mapping]] = ..., pinnedDialogsChanged: _Optional[_Union[WebPinnedDialogsChanged, _Mapping]] = ..., messageReactionsReadByMe: _Optional[_Union[WebMessageReactionsReadByMe, _Mapping]] = ..., messageNewReaction: _Optional[_Union[WebMessageNewReaction, _Mapping]] = ..., callEvent: _Optional[_Union[WebCallEvent, _Mapping]] = ..., startLive: _Optional[_Union[WebStartLive, _Mapping]] = ..., endLive: _Optional[_Union[WebEndLive, _Mapping]] = ..., folderCreated: _Optional[_Union[WebFolderCreated, _Mapping]] = ..., folderDeleted: _Optional[_Union[WebFolderDeleted, _Mapping]] = ..., foldersReordered: _Optional[_Union[WebFoldersReordered, _Mapping]] = ..., dialogsMarkedAsRead: _Optional[_Union[WebDialogsMarkedAsRead, _Mapping]] = ..., dialogsMarkedAsUnread: _Optional[_Union[WebDialogsMarkedAsUnread, _Mapping]] = ..., folderEdited: _Optional[_Union[WebFolderEdited, _Mapping]] = ..., callAction: _Optional[_Union[WebCallAction, _Mapping]] = ..., dialogsUnpinned: _Optional[_Union[WebDialogsUnpinned, _Mapping]] = ..., messagePinned: _Optional[_Union[WebMessagePinned, _Mapping]] = ..., messagesUnPinned: _Optional[_Union[WebMessagesUnPinned, _Mapping]] = ..., transcriptReady: _Optional[_Union[WebTranscriptReady, _Mapping]] = ..., generalNotificationMessage: _Optional[_Union[WebGeneralNotificationMessage, _Mapping]] = ..., askBotReview: _Optional[_Union[WebAskBotReview, _Mapping]] = ..., dialogArchiveStatus: _Optional[_Union[WebDialogArchiveStatus, _Mapping]] = ..., premiumPurchaseStatus: _Optional[_Union[WebPremiumPurchaseStatus, _Mapping]] = ..., endpointChanged: _Optional[_Union[WebEndpointChanged, _Mapping]] = ..., topicCreated: _Optional[_Union[WebTopicCreated, _Mapping]] = ..., topicEdited: _Optional[_Union[WebTopicEdited, _Mapping]] = ..., topicDeleted: _Optional[_Union[WebTopicDeleted, _Mapping]] = ..., messageStreamChunks: _Optional[_Union[WebMessageStreamChunks, _Mapping]] = ..., peerHaveScheduleTask: _Optional[_Union[WebPeerHaveScheduleTask, _Mapping]] = ..., allContactsRemoved: _Optional[_Union[WebAllContactsRemoved, _Mapping]] = ..., requestBankiAccessFor: _Optional[_Union[WebRequestBankiAccessFor, _Mapping]] = ..., walletUpdated: _Optional[_Union[WebWalletUpdated, _Mapping]] = ..., walletBalanceUpdated: _Optional[_Union[WebWalletBalanceUpdated, _Mapping]] = ...) -> None: ...

class WebUser(_message.Message):
    __slots__ = ("id", "accessHash", "name", "localName", "sex", "avatar", "isBot", "nick", "ext", "stateVersion", "isDeleted", "contactInfo", "puppeteer", "createdAt", "exInfo", "botExInfo")
    class ExtEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    ACCESSHASH_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LOCALNAME_FIELD_NUMBER: _ClassVar[int]
    SEX_FIELD_NUMBER: _ClassVar[int]
    AVATAR_FIELD_NUMBER: _ClassVar[int]
    ISBOT_FIELD_NUMBER: _ClassVar[int]
    NICK_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    STATEVERSION_FIELD_NUMBER: _ClassVar[int]
    ISDELETED_FIELD_NUMBER: _ClassVar[int]
    CONTACTINFO_FIELD_NUMBER: _ClassVar[int]
    PUPPETEER_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    EXINFO_FIELD_NUMBER: _ClassVar[int]
    BOTEXINFO_FIELD_NUMBER: _ClassVar[int]
    id: int
    accessHash: int
    name: str
    localName: WebStringValue
    sex: int
    avatar: WebAvatar
    isBot: WebBoolValue_1
    nick: WebStringValue
    ext: _containers.ScalarMap[str, bytes]
    stateVersion: WebInt64Value_1
    isDeleted: WebBoolValue_1
    contactInfo: _containers.RepeatedCompositeFieldContainer[WebContactInfo]
    puppeteer: int
    createdAt: WebInt64Value_1
    exInfo: WebExInfo
    botExInfo: WebBotExInfo
    def __init__(self, id: _Optional[int] = ..., accessHash: _Optional[int] = ..., name: _Optional[str] = ..., localName: _Optional[_Union[WebStringValue, _Mapping]] = ..., sex: _Optional[int] = ..., avatar: _Optional[_Union[WebAvatar, _Mapping]] = ..., isBot: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., nick: _Optional[_Union[WebStringValue, _Mapping]] = ..., ext: _Optional[_Mapping[str, bytes]] = ..., stateVersion: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., isDeleted: _Optional[_Union[WebBoolValue_1, _Mapping]] = ..., contactInfo: _Optional[_Iterable[_Union[WebContactInfo, _Mapping]]] = ..., puppeteer: _Optional[int] = ..., createdAt: _Optional[_Union[WebInt64Value_1, _Mapping]] = ..., exInfo: _Optional[_Union[WebExInfo, _Mapping]] = ..., botExInfo: _Optional[_Union[WebBotExInfo, _Mapping]] = ...) -> None: ...

class WebUserAboutChanged(_message.Message):
    __slots__ = ("uid", "about")
    UID_FIELD_NUMBER: _ClassVar[int]
    ABOUT_FIELD_NUMBER: _ClassVar[int]
    uid: int
    about: WebStringValue
    def __init__(self, uid: _Optional[int] = ..., about: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebUserAdministratorRights(_message.Message):
    __slots__ = ("isAnonymous", "canManageChat", "canDeleteMessages", "canManageVideoChats", "canRestrictMembers", "canPromoteMembers", "canChangeInfo", "canInviteUsers", "canPostMessages", "canEditMessages", "canPinMessages", "canManageTopics")
    ISANONYMOUS_FIELD_NUMBER: _ClassVar[int]
    CANMANAGECHAT_FIELD_NUMBER: _ClassVar[int]
    CANDELETEMESSAGES_FIELD_NUMBER: _ClassVar[int]
    CANMANAGEVIDEOCHATS_FIELD_NUMBER: _ClassVar[int]
    CANRESTRICTMEMBERS_FIELD_NUMBER: _ClassVar[int]
    CANPROMOTEMEMBERS_FIELD_NUMBER: _ClassVar[int]
    CANCHANGEINFO_FIELD_NUMBER: _ClassVar[int]
    CANINVITEUSERS_FIELD_NUMBER: _ClassVar[int]
    CANPOSTMESSAGES_FIELD_NUMBER: _ClassVar[int]
    CANEDITMESSAGES_FIELD_NUMBER: _ClassVar[int]
    CANPINMESSAGES_FIELD_NUMBER: _ClassVar[int]
    CANMANAGETOPICS_FIELD_NUMBER: _ClassVar[int]
    isAnonymous: bool
    canManageChat: bool
    canDeleteMessages: bool
    canManageVideoChats: bool
    canRestrictMembers: bool
    canPromoteMembers: bool
    canChangeInfo: bool
    canInviteUsers: bool
    canPostMessages: bool
    canEditMessages: bool
    canPinMessages: bool
    canManageTopics: bool
    def __init__(self, isAnonymous: _Optional[bool] = ..., canManageChat: _Optional[bool] = ..., canDeleteMessages: _Optional[bool] = ..., canManageVideoChats: _Optional[bool] = ..., canRestrictMembers: _Optional[bool] = ..., canPromoteMembers: _Optional[bool] = ..., canChangeInfo: _Optional[bool] = ..., canInviteUsers: _Optional[bool] = ..., canPostMessages: _Optional[bool] = ..., canEditMessages: _Optional[bool] = ..., canPinMessages: _Optional[bool] = ..., canManageTopics: _Optional[bool] = ...) -> None: ...

class WebUserAvatarChanged(_message.Message):
    __slots__ = ("uid", "avatar", "avatars")
    UID_FIELD_NUMBER: _ClassVar[int]
    AVATAR_FIELD_NUMBER: _ClassVar[int]
    AVATARS_FIELD_NUMBER: _ClassVar[int]
    uid: int
    avatar: WebAvatar
    avatars: WebAvatars
    def __init__(self, uid: _Optional[int] = ..., avatar: _Optional[_Union[WebAvatar, _Mapping]] = ..., avatars: _Optional[_Union[WebAvatars, _Mapping]] = ...) -> None: ...

class WebUserBlocked(_message.Message):
    __slots__ = ("uid",)
    UID_FIELD_NUMBER: _ClassVar[int]
    uid: int
    def __init__(self, uid: _Optional[int] = ...) -> None: ...

class WebUserBotCommandsChanged(_message.Message):
    __slots__ = ("uid", "commands")
    UID_FIELD_NUMBER: _ClassVar[int]
    COMMANDS_FIELD_NUMBER: _ClassVar[int]
    uid: int
    commands: _containers.RepeatedCompositeFieldContainer[WebBotCommand]
    def __init__(self, uid: _Optional[int] = ..., commands: _Optional[_Iterable[_Union[WebBotCommand, _Mapping]]] = ...) -> None: ...

class WebUserContactsChanged(_message.Message):
    __slots__ = ("uid", "contactRecords")
    UID_FIELD_NUMBER: _ClassVar[int]
    CONTACTRECORDS_FIELD_NUMBER: _ClassVar[int]
    uid: int
    contactRecords: _containers.RepeatedCompositeFieldContainer[WebContactInfo]
    def __init__(self, uid: _Optional[int] = ..., contactRecords: _Optional[_Iterable[_Union[WebContactInfo, _Mapping]]] = ...) -> None: ...

class WebUserDefaultBankAccountChanged(_message.Message):
    __slots__ = ("uid", "defaultBankAccount")
    UID_FIELD_NUMBER: _ClassVar[int]
    DEFAULTBANKACCOUNT_FIELD_NUMBER: _ClassVar[int]
    uid: int
    defaultBankAccount: WebStringValue
    def __init__(self, uid: _Optional[int] = ..., defaultBankAccount: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebUserDefaultCardNumberChanged(_message.Message):
    __slots__ = ("uid", "defaultCardNumber")
    UID_FIELD_NUMBER: _ClassVar[int]
    DEFAULTCARDNUMBER_FIELD_NUMBER: _ClassVar[int]
    uid: int
    defaultCardNumber: WebStringValue
    def __init__(self, uid: _Optional[int] = ..., defaultCardNumber: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebUserDefaultCardNumberRemoved(_message.Message):
    __slots__ = ("uid",)
    UID_FIELD_NUMBER: _ClassVar[int]
    uid: int
    def __init__(self, uid: _Optional[int] = ...) -> None: ...

class WebUserExInfoChanged(_message.Message):
    __slots__ = ("uid", "exInfo")
    UID_FIELD_NUMBER: _ClassVar[int]
    EXINFO_FIELD_NUMBER: _ClassVar[int]
    uid: int
    exInfo: WebExInfo
    def __init__(self, uid: _Optional[int] = ..., exInfo: _Optional[_Union[WebExInfo, _Mapping]] = ...) -> None: ...

class WebUserExtChanged(_message.Message):
    __slots__ = ("uid", "ext")
    UID_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    uid: int
    ext: WebExt
    def __init__(self, uid: _Optional[int] = ..., ext: _Optional[_Union[WebExt, _Mapping]] = ...) -> None: ...

class WebUserFullExtChanged(_message.Message):
    __slots__ = ("uid", "ext")
    UID_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    uid: int
    ext: WebExt
    def __init__(self, uid: _Optional[int] = ..., ext: _Optional[_Union[WebExt, _Mapping]] = ...) -> None: ...

class WebUserLastSeen(_message.Message):
    __slots__ = ("uid", "date", "deviceType", "deviceCategory")
    UID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    DEVICETYPE_FIELD_NUMBER: _ClassVar[int]
    DEVICECATEGORY_FIELD_NUMBER: _ClassVar[int]
    uid: int
    date: int
    deviceType: int
    deviceCategory: WebStringValue
    def __init__(self, uid: _Optional[int] = ..., date: _Optional[int] = ..., deviceType: _Optional[int] = ..., deviceCategory: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebUserLastSeenUnknown(_message.Message):
    __slots__ = ("uid", "deviceType", "deviceCategory", "date")
    UID_FIELD_NUMBER: _ClassVar[int]
    DEVICETYPE_FIELD_NUMBER: _ClassVar[int]
    DEVICECATEGORY_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    uid: int
    deviceType: int
    deviceCategory: WebStringValue
    date: WebInt64Value_1
    def __init__(self, uid: _Optional[int] = ..., deviceType: _Optional[int] = ..., deviceCategory: _Optional[_Union[WebStringValue, _Mapping]] = ..., date: _Optional[_Union[WebInt64Value_1, _Mapping]] = ...) -> None: ...

class WebUserLocalNameChanged(_message.Message):
    __slots__ = ("uid", "localName")
    UID_FIELD_NUMBER: _ClassVar[int]
    LOCALNAME_FIELD_NUMBER: _ClassVar[int]
    uid: int
    localName: WebStringValue
    def __init__(self, uid: _Optional[int] = ..., localName: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebUserNameChanged(_message.Message):
    __slots__ = ("uid", "name")
    UID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    uid: int
    name: str
    def __init__(self, uid: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class WebUserNickChanged(_message.Message):
    __slots__ = ("uid", "nickname")
    UID_FIELD_NUMBER: _ClassVar[int]
    NICKNAME_FIELD_NUMBER: _ClassVar[int]
    uid: int
    nickname: WebStringValue
    def __init__(self, uid: _Optional[int] = ..., nickname: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebUserOffline(_message.Message):
    __slots__ = ("uid", "deviceType", "deviceCategory")
    UID_FIELD_NUMBER: _ClassVar[int]
    DEVICETYPE_FIELD_NUMBER: _ClassVar[int]
    DEVICECATEGORY_FIELD_NUMBER: _ClassVar[int]
    uid: int
    deviceType: int
    deviceCategory: WebStringValue
    def __init__(self, uid: _Optional[int] = ..., deviceType: _Optional[int] = ..., deviceCategory: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebUserOnline(_message.Message):
    __slots__ = ("uid", "deviceType", "deviceCategory")
    UID_FIELD_NUMBER: _ClassVar[int]
    DEVICETYPE_FIELD_NUMBER: _ClassVar[int]
    DEVICECATEGORY_FIELD_NUMBER: _ClassVar[int]
    uid: int
    deviceType: int
    deviceCategory: WebStringValue
    def __init__(self, uid: _Optional[int] = ..., deviceType: _Optional[int] = ..., deviceCategory: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebUserPeer(_message.Message):
    __slots__ = ("uid", "accessHash")
    UID_FIELD_NUMBER: _ClassVar[int]
    ACCESSHASH_FIELD_NUMBER: _ClassVar[int]
    uid: int
    accessHash: int
    def __init__(self, uid: _Optional[int] = ..., accessHash: _Optional[int] = ...) -> None: ...

class WebUserPreferredLanguagesChanged(_message.Message):
    __slots__ = ("uid", "preferredLanguages")
    UID_FIELD_NUMBER: _ClassVar[int]
    PREFERREDLANGUAGES_FIELD_NUMBER: _ClassVar[int]
    uid: int
    preferredLanguages: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, uid: _Optional[int] = ..., preferredLanguages: _Optional[_Iterable[str]] = ...) -> None: ...

class WebUserTimeZoneChanged(_message.Message):
    __slots__ = ("uid", "timeZone")
    UID_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    uid: int
    timeZone: WebStringValue
    def __init__(self, uid: _Optional[int] = ..., timeZone: _Optional[_Union[WebStringValue, _Mapping]] = ...) -> None: ...

class WebUserUnblocked(_message.Message):
    __slots__ = ("uid",)
    UID_FIELD_NUMBER: _ClassVar[int]
    uid: int
    def __init__(self, uid: _Optional[int] = ...) -> None: ...

class WebValue(_message.Message):
    __slots__ = ("stringValue", "booleanValue", "int32Value", "int64Value", "doubleValue", "arrayValue")
    STRINGVALUE_FIELD_NUMBER: _ClassVar[int]
    BOOLEANVALUE_FIELD_NUMBER: _ClassVar[int]
    INT32VALUE_FIELD_NUMBER: _ClassVar[int]
    INT64VALUE_FIELD_NUMBER: _ClassVar[int]
    DOUBLEVALUE_FIELD_NUMBER: _ClassVar[int]
    ARRAYVALUE_FIELD_NUMBER: _ClassVar[int]
    stringValue: str
    booleanValue: bool
    int32Value: int
    int64Value: int
    doubleValue: float
    arrayValue: WebList
    def __init__(self, stringValue: _Optional[str] = ..., booleanValue: _Optional[bool] = ..., int32Value: _Optional[int] = ..., int64Value: _Optional[int] = ..., doubleValue: _Optional[float] = ..., arrayValue: _Optional[_Union[WebList, _Mapping]] = ...) -> None: ...

class WebVitrineChanged(_message.Message):
    __slots__ = ("version",)
    VERSION_FIELD_NUMBER: _ClassVar[int]
    version: str
    def __init__(self, version: _Optional[str] = ...) -> None: ...

class WebWalletBalanceUpdated(_message.Message):
    __slots__ = ("walletId", "newBalance")
    WALLETID_FIELD_NUMBER: _ClassVar[int]
    NEWBALANCE_FIELD_NUMBER: _ClassVar[int]
    walletId: str
    newBalance: WebBalance
    def __init__(self, walletId: _Optional[str] = ..., newBalance: _Optional[_Union[WebBalance, _Mapping]] = ...) -> None: ...

class WebWalletType(_message.Message):
    __slots__ = ("id", "balances", "walletLink", "isActive")
    ID_FIELD_NUMBER: _ClassVar[int]
    BALANCES_FIELD_NUMBER: _ClassVar[int]
    WALLETLINK_FIELD_NUMBER: _ClassVar[int]
    ISACTIVE_FIELD_NUMBER: _ClassVar[int]
    id: str
    balances: _containers.RepeatedCompositeFieldContainer[WebBalance]
    walletLink: WebStringValue
    isActive: WebBoolValue_1
    def __init__(self, id: _Optional[str] = ..., balances: _Optional[_Iterable[_Union[WebBalance, _Mapping]]] = ..., walletLink: _Optional[_Union[WebStringValue, _Mapping]] = ..., isActive: _Optional[_Union[WebBoolValue_1, _Mapping]] = ...) -> None: ...

class WebWalletUpdated(_message.Message):
    __slots__ = ("newWallet",)
    NEWWALLET_FIELD_NUMBER: _ClassVar[int]
    newWallet: WebWalletType
    def __init__(self, newWallet: _Optional[_Union[WebWalletType, _Mapping]] = ...) -> None: ...

class WebWebApp(_message.Message):
    __slots__ = ("url",)
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str
    def __init__(self, url: _Optional[str] = ...) -> None: ...
