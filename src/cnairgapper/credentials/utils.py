def get_credential(dictionary: dict, key_path: str, separator: str = ".") -> any:
    """Retrieve a value from a nested dictionary using a key path.

    This function navigates through a nested dictionary using the provided key
    path and separator to retrieve the desired value. If any part of the path
    is not found or is not a dictionary, the function returns None.

    :param dictionary: The nested dictionary to traverse.
    :param key_path: A string representing the path of keys separated by the
        specified separator.
    :param separator: The character used to separate keys in the path. Defaults to ".".
    :return: The value found at the specified key path, or None if the path is not
        valid or does not exist.

    :rtype: any

    :raises: This function does not raise exceptions but returns None if the
        traversal fails.

    :example:
        >>> data = {'user': {'credentials': {'username': 'admin', 'password': '1234'}}}
        >>> key_path = 'user.credentials.username'
        >>> get_credential(data, key_path)
        'admin'

        >>> get_credential(data, 'user.name')
        None

        >>> get_credential(data, 'user.credentials.username', separator='.')
        'admin'

    """
    current = dictionary
    if not key_path:
        return current

    for key in key_path.split(separator):
        if not isinstance(current, dict):
            return None
        current = current.get(key)
        if current is None:
            return None

    return current
