# -*- coding: utf-8 -*-

from sqlalchemy.dialects import postgresql
from sqlalchemy import types

from forest.common import utils


class IPAddress(types.TypeDecorator):
    """An SQLAlchemy type representing an IP-address."""
    impl = types.String(39).with_variant(postgresql.INET(), 'postgresql')

    def process_bind_param(self, value, dialect):
        """Process/Formats the value before insert it into the db."""
        if dialect.name == 'postgresql':
            return value
        # NOTE(maurosr): The purpose here is to convert ipv6 to the shortened
        # form, not validate it.
        elif utils.is_valid_ipv6(value):
            return utils.get_shortened_ipv6(value)
        return value


class CIDR(types.TypeDecorator):
    """An SQLAlchemy type representing a CIDR definition."""
    impl = types.String(43).with_variant(postgresql.INET(), 'postgresql')

    def process_bind_param(self, value, dialect):
        """Process/Formats the value before insert it into the db."""
        # NOTE(sdague): normalize all the inserts
        if utils.is_valid_ipv6_cidr(value):
            return utils.get_shortened_ipv6_cidr(value)
        return value
