# -*- coding: utf-8 -*-
import re
from typing import Any

"""

Implementation example dedicated to aspect-oriented programming in Python.

No optimizations that would be premature.
If you want to use a real aspect-oriented programming with python,
there are some well-maintained projects in appropriate repositories on the Internet. 
It is better to use one of these than re-invent the wheel.
"""


class Spectator(type):
    """
    Metaclass used by classes that will have aspect-oriented methods (with the join-points and cross-cut points and etc.
    The aspect-rules property contains all the aspect rules
    """
    aspect_rules = []
    wrapped_methods = []

    def __new__(mcs, name, bases, dict):
        """
        Class initialization that contains aspect-oriented methods.
        It basically annotates all methods of the class so that every call can be checked
        if there is a corresponding rule to them:
        """
        for key, value in dict.items():
            if hasattr(value, "__call__") and key != "__metaclass__":
                dict[key] = Spectator.wrap_method(value)

        return type.__new__(mcs, name, bases, dict)

    @classmethod
    def register(mcs, name_pattern="", in_objects=(), out_objects=(), before=None, after=None):
        """
        Method used to register a new aspect rule.
        Logging can be done dynamically at run time
        
        name_pattern: is a regular expression that matches the names of the methods. blank, home with all methods.

        In particular, note that this simplified scheme does not account for to call a pre_function based on out_objects
        """
        # So simple method that could be used a direct append in "aspect rules"
        rule = {
            "name_pattern": name_pattern,
            "in_objects": in_objects,
            "out_objects": out_objects,
            "pre": before,
            "post": after}
        mcs.aspect_rules.append(rule)

    @classmethod
    def wrap_method(mcs, method):
        def call(*args, **kw):
            before_funcs = mcs.matching_before(method, args, kw)
            for func in before_funcs:
                func(*args, **kw)

            results = method(*args, **kw)
            after_funcs = mcs.matching_after(method, results)
            for func in after_funcs:
                func(results, *args, **kw)

            return results

        return call

    @classmethod
    def matching_names(mcs, method):
        return [rule for rule in mcs.aspect_rules
                if re.match(rule["name_pattern"], method.__name__) or rule["name_pattern"] == ""]

    @classmethod
    def matching_before(mcs, method, args, kw):
        all_args = args + tuple(kw.values())

        return [rule["pre"] for rule in mcs.matching_names(method)
                if rule["pre"] and (rule["in_objects"] == () or any((type(arg) in rule["in_objects"]
                                                                     for arg in all_args)))]

    @classmethod
    def matching_after(mcs, method, results):
        if type(results) is not tuple:
            results = (results,)

        return [rule["post"] for rule in mcs.matching_names(method)
                if rule["post"] and (rule["out_objects"] == () or any((type(result) in rule["out_objects"]
                                                                       for result in results)))]


# testing
class Address(object):
    def __repr__(self):
        return "Address..."


class Person(object, metaclass=Spectator):
    def update_address(self, address):
        pass

    def __str__(self):
        return "person object"


def log_update(*args, **kw):
    print("Updating object %s" % str(args[0]))


def log_address(*args, **kw):
    addresses = [arg for arg in (args + tuple(kw.values()))
                 if type(arg) is Address]
    print(addresses)


class Experiment(metaclass=Spectator):
    def __init__(self):
        self._value = None

    @property
    def value(self) -> Any:
        return self._value

    def set_value(self, value):
        self._value = value


class Integer(metaclass=Spectator):
    def __init__(self):
        self._value = 0

    @property
    def value(self) -> Any:
        return self._value

    def set_value(self, value: int):
        self._value = value


def before_set_value(*args, **kw):
    print('Before set value: %s %s' % (args, kw))


def after_set_value(*args, **kw):
    print('After set value: %s %s' % (args, kw))


if __name__ == "__main__":
    Spectator.register(name_pattern="^update.*", before=log_update)
    Spectator.register(in_objects=(Address,), before=log_address)

    p = Person()
    p.update_address(Address())

    Spectator.register(name_pattern='set_value', before=before_set_value, after=after_set_value)

    e = Experiment()
    e.set_value('v1')

    i = Integer()
    i.set_value(5)
