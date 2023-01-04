import argparse
import os
import uuid

def valid_move(move):
    """
    Check if the move is a valid move.

    Args:
        move (str): the move to be checked.

    Returns:
        str: the move if it is valid.

    Raises:
        argparse.ArgumentTypeError: if the move is not valid.
    """
    # check if the move is one of the valid moves
    if move not in ['rock', 'paper', 'scissors']:
        # raise an ArgumentTypeError if the move is not valid
        raise argparse.ArgumentTypeError('Invalid move: %s' % move)
    # return the move if it is valid
    return move


def valid_round(round):
    """
    Check if the round number is a valid round number.

    Args:
        round (int): the round number to be checked.

    Returns:
        int: the round number if it is valid.

    Raises:
        argparse.ArgumentTypeError: if the round number is not valid.
    """
    # convert the round argument to an integer
    round = int(round)
    # check if the round number is a positive integer
    if round <= 0 or not isinstance(round, int):
        # raise an ArgumentTypeError if the round number is not valid
        raise argparse.ArgumentTypeError('Invalid round number: %s' % round)
    # return the round number if it is valid
    return str(round)


def valid_file_path(file_path):
    """
    Check if the file path is a valid file path.

    Args:
        file_path (str): the file path to be checked.

    Returns:
        str: the file path if it is valid.

    Raises:
        argparse.ArgumentTypeError: if the file path is not valid.
    """
    # check if the file path exists and is a file
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        # raise an ArgumentTypeError if the file path is not valid
        raise argparse.ArgumentTypeError('Invalid file path: %s' % file_path)
    # return the file path if it is valid
    return file_path


def valid_client_id(client_id):
    """
    Check if the client ID is a valid client ID.

    Args:
        client_id (str): the client ID to be checked.

    Returns:
        str: the client ID if it is valid.

    Raises:
        argparse.ArgumentTypeError: if the client ID is not valid.
    """
    try:
        # parse the client ID and check if it is a valid UUID
        uuid.UUID(client_id)
    except ValueError:
        # raise an ArgumentTypeError if the client ID is not valid
        raise argparse.ArgumentTypeError('Invalid client ID: %s' % client_id)
    # return the client ID if it is valid
    return client_id

