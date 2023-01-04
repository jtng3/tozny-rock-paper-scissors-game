import argparse
import json
import os
import uuid
import e3db


def valid_move(move):
    """
    Check if the move is a valid move.

    Args:
        move (str): the move to be checked.

    Returns:
        str: the move if it is valid, always in lowercase

    Raises:
        argparse.ArgumentTypeError: if the move is not valid.
    """
    move = move.lower() # convert move to lowercase
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
    if round <= 0:
        # raise an ArgumentTypeError if the round number is not valid
        raise argparse.ArgumentTypeError('Invalid round number: %s' % round)
    # return the round number if it is valid as a string
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


def parse_args():
    """
    Parse the command line arguments.

    Returns:
        An object containing the parsed arguments.
    """
    # create an argument parser
    parser = argparse.ArgumentParser()

    # add the round number and client credentials filepath arguments
    parser.add_argument('round', type=valid_round,
                        help='the round number')
    parser.add_argument('tozny_client_credentials_filepath', type=valid_file_path,
                        help='the file path to the player\'s Tozny client credentials')

    # parse the command line arguments
    return parser.parse_args()

def parse_args_for_gameplay():
    """
    Parse the command line arguments for gameplay

    Returns:
        An object containing the parsed arguments.
    """
    # create an argument parser
    parser = argparse.ArgumentParser()

    # add the round number, player name, move, and client credentials filepath arguments
    parser.add_argument('round', type=valid_round,
                        help='the round number')
    parser.add_argument('name', type=str,
                        help='the player name')
    parser.add_argument('move', type=valid_move,
                        help='the player move')
    parser.add_argument('tozny_client_credentials_filepath', type=valid_file_path,
                        help='the file path to the player\'s Tozny client credentials')

    # add an optional judge client ID argument
    parser.add_argument('--judge_id', type=valid_client_id,
                        help='the client ID of Judge Clarence')

    # parse the command line arguments
    return parser.parse_args()


def load_client_credentials(filepath):
    """
    Load client credentials from a file.

    Args:
        filepath: The file path to the client credentials.

    Returns:
        A dictionary containing the client credentials.

    Raises:
        RuntimeError: If there was an error loading the client credentials from the file.
    """
    # try to load the client credentials from the file
    try:
        with open(filepath, 'r') as f:
            client_info = json.load(f)
    # handle any potential errors
    except (IOError, json.JSONDecodeError) as e:
        raise RuntimeError(
            'Error loading client credentials from file: %s' % e)
    return client_info


def create_client(client_info):
    """
    Create a e3db.Client instance.

    Args:
        client_info: A dictionary containing the client credentials.

    Returns:
        A e3db.Client instance.
    """
    # create a Config instance using the client credentials
    config = e3db.Config(
        client_info["client_id"],
        client_info["api_key_id"],
        client_info["api_secret"],
        client_info["public_key"],
        client_info["private_key"]
    )
    # return a new Client instance using the Config instance
    return e3db.Client(config())

def share_record_type(client, record_type, client_id):
    """
    Share a record type with the specified client.

    Args:
        client: A e3db.Client instance.
        record_type: The type of the record to share.
        client_id: The client ID of the recipient.

    Raises:
        RuntimeError: If there was an error sharing the record.
    """
    try:
        # share the record with the specified client
        client.share(record_type, client_id)
    except Exception as e:
        raise RuntimeError("Error sharing record with Judge: %s" % e)