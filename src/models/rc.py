from dataclasses import dataclass


@dataclass
class RC:
    """
    Represents a response code with various attributes indicating the state,
    messages, and related information.

    This data class is used to encapsulate the response status that can include
    flags for success, error, synchronization count, and additional metadata such
    as messages, status, type, references, and associated entities.

    Attributes:
        ok: A boolean flag indicating if the response is successful.
        err: A boolean flag indicating if there was an error in the response.
        sync_cnt: A boolean flag representing if the synchronization count is enabled.
        msg: A string containing any relevant message or feedback.
        ref: A string reference associated with this response.
        status: A string representing the status of the response.
        type: A string defining the type of the response.
        entity: Represents an associated entity or object tied to this response.
    """

    ok: bool = False
    err: bool = False
    sync_cnt: bool = False
    msg: str = ""
    ref: str = ""
    type: str = ""
    entity: any = None


def print_rc(rc: RC):
    """
    Prints the synchronization status of RC entities grouped by their type.

    This function processes the given RC object, which contains a collection
    of entities, each having attributes such as type, synchronization count,
    and status (ok or nok). It aggregates the entities' statuses by their
    type, counts them based on their success or failure, and outputs this
    information in a structured and comprehensible format. Entities marked
    as 'ok' or 'nok' will also have their details printed accordingly.

    Args:
        rc (RC): The RC object containing a collection of entities to
                 process and analyze.

    Returns:
        None

    Raises:
        None
    """
    status = {}
    for _rc in rc.entity:
        if not _rc.sync_cnt:
            continue
        if _rc.type not in status:
            status[_rc.type] = {"ok": {"cnt": 0, "items": []}, "nok": {"cnt": 0, "items": []}}
        if _rc.ok:
            status[_rc.type]["ok"]["cnt"] += 1
            status[_rc.type]["ok"]["items"].append(_rc)
        else:
            status[_rc.type]["nok"]["cnt"] += 1
            status[_rc.type]["nok"]["items"].append(_rc)
    for _type, _info in status.items():
        print(f"{_type} - ok:{_info['ok']['cnt']} nok:{_info['nok']['cnt']}")
        for entity in _info["ok"]["items"]:
            print(f" [OK] - {str(entity.ref)}")
        for entity in _info["nok"]["items"]:
            print(f" [NOK]- {str(entity.ref)} : {str(entity.msg)}")
