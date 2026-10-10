"""Exceptions never include credentials or signed media URLs."""


class BaleError(Exception):
    pass


class AuthenticationError(BaleError):
    pass


class PasswordRequired(AuthenticationError):
    def __init__(self, challenge):
        super().__init__("Account password required; call complete_password_login with this challenge")
        self.challenge = challenge


class BatchDownloadError(BaleError):
    def __init__(self, results):
        super().__init__("Some media downloads failed; inspect ordered results")
        self.results = tuple(results)


class ClientClosed(BaleError):
    pass


class ConversationClosed(BaleError):
    pass


class HistoryPaginationGap(BaleError):
    """A timestamp-only server cursor cannot prove a complete boundary page."""

    def __init__(self, peer, date: int):
        super().__init__("History timestamp boundary exceeds the verified pagination capacity")
        self.peer, self.date = peer, date


class SearchSnapshotUnavailable(BaleError):
    """The indexed reference could not be hydrated from the bounded history window."""

    def __init__(self, ref):
        super().__init__("Indexed match has no full snapshot in the bounded history window")
        self.ref = ref


class GroupCreationIncomplete(BaleError):
    """Creation succeeded, but the server rejected some requested member additions."""

    def __init__(self, peer, rejected_user_ids):
        super().__init__("Group was created, but some member additions were rejected")
        self.peer, self.rejected_user_ids = peer, tuple(rejected_user_ids)


class PeerNotFound(BaleError):
    pass


class PeerKindRequired(BaleError):
    pass


class ProtocolError(BaleError):
    pass


class StorageError(BaleError):
    pass


class IdempotencyConflict(BaleError):
    pass


class SessionInUse(BaleError):
    pass


class TransportError(BaleError):
    def __init__(self, message: str, *, possibly_sent: bool = False):
        super().__init__(message)
        self.possibly_sent = possibly_sent


class RpcError(BaleError):
    def __init__(self, code: int, method: str, *, retry_after: float | None = None, reason: str = ""):
        super().__init__(f"RPC {method} failed with code {code}")
        self.code, self.method, self.retry_after = code, method, retry_after
        self.reason = reason


class DeliveryUncertain(BaleError):
    def __init__(self, operation_id: str):
        super().__init__(f"Delivery is uncertain; inspect operation {operation_id}")
        self.operation_id = operation_id


class OperationFailed(BaleError):
    def __init__(self, operation_id: str, reason: str):
        super().__init__(f"Operation {operation_id}: {reason}")
        self.operation_id = operation_id


class MessageReferencesUnavailable(BaleError):
    """Delivery is confirmed, but exact per-item references could not be hydrated."""

    def __init__(self, operation_id: str):
        super().__init__(
            f"Delivery confirmed; exact message references unavailable for operation {operation_id}"
        )
        self.operation_id = operation_id
