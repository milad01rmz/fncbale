"""Account-local bounded identity cache; aliases never outlive their owner."""

from collections import OrderedDict
from collections.abc import Mapping
import time

from .models import Peer


class PeerCache(Mapping[str, tuple[float, Peer]]):
    def __init__(self, limit: int):
        self.limit = limit
        self._entries: OrderedDict[str, tuple[float, Peer]] = OrderedDict()
        self._aliases: dict[str, str] = {}
        self._sweep_at = 0.0

    @staticmethod
    def _alias(peer):
        return "@" + peer.username.lower().lstrip("@") if peer.username else None

    @property
    def peer_count(self):
        return len(self._entries)

    @property
    def alias_count(self):
        return len(self._aliases)

    def discard(self, key):
        owner = self._aliases.get(key, key)
        entry = self._entries.pop(owner, None)
        if entry is not None:
            alias = self._alias(entry[1])
            if alias is not None and self._aliases.get(alias) == owner:
                del self._aliases[alias]

    def put(self, peer, expires):
        now = time.monotonic()
        if now >= self._sweep_at:
            self.prune(now)
        self.discard(peer.key)
        alias = self._alias(peer)
        if alias is not None:
            # A newer authoritative identity cannot leave the old alias owner
            # available with the same obsolete username/hash metadata.
            self.discard(alias)
        if expires <= now:
            return
        self._entries[peer.key] = (expires, peer)
        if alias is not None:
            self._aliases[alias] = peer.key
        if len(self._entries) > self.limit:
            self.discard(next(iter(self._entries)))

    def __getitem__(self, key):
        owner = self._aliases.get(key, key)
        entry = self._entries[owner]
        if entry[0] <= time.monotonic():
            self.discard(owner)
            raise KeyError(key)
        self._entries.move_to_end(owner)
        return entry

    def __iter__(self):
        self.prune()
        # Expiration during a Mapping view iteration must not mutate its iterator.
        return iter((*self._entries, *self._aliases))

    def __len__(self):
        return len(self._entries) + len(self._aliases)

    def pop(self, key, default=None):
        try:
            entry = self[key]
        except KeyError:
            return default
        self.discard(key)
        return entry

    def prune(self, now=None):
        now = time.monotonic() if now is None else now
        expired = [key for key, entry in self._entries.items() if entry[0] <= now]
        for key in expired:
            self.discard(key)
        self._sweep_at = now + 1.0

    def clear(self):
        self._entries.clear()
        self._aliases.clear()
        self._sweep_at = 0.0
