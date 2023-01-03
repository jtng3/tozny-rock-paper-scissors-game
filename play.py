import argparse
import json
import os
import e3db
import uuid
from e3db.types import Search


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
    # check if the round number is a positive integer
    if round <= 0 or not isinstance(round, int):
        # raise an ArgumentTypeError if the round number is not valid
        raise argparse.ArgumentTypeError('Invalid round number: %s' % round)
    # return the round number if it is valid
    return round


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


def main():
    # create an argument parser
    parser = argparse.ArgumentParser()

    # add the round number, player name, and move arguments
    parser.add_argument('round', type=valid_round, required=True,
                        help='the round number')
    parser.add_argument('name', type=str, required=True,
                        help='the player name')
    parser.add_argument('move', type=valid_move, required=True,
                        help='the player move')
    parser.add_argument('tozny_client_credentials_filepath', type=valid_file_path, required=True,
                        help='the file path to the player\'s Tozny client credentials')

    # add an optional client ID argument
    parser.add_argument('--client_id', type=valid_client_id help='the client ID of Judge Clarence')

    # parse the command line arguments
    args = parser.parse_args()

    # use the hardcoded client ID if the optional argument was not provided
    judge_client_id = args.client_id or 'hardcoded_client_id'

    # try to load the Tozny client credentials from the file
    try:
        with open(args.tozny_client_credentials_filepath, 'r') as f:
            client_info = json.load(f)
    # handle any potential errors
    except (IOError, json.JSONDecodeError) as e:
        print('Error:', e)
        exit(1)

    # pass credientials into the configuration constructor
    config = e3db.Config(
        client_info["client_id"],
        client_info["api_key_id"],
        client_info["api_secret"],
        client_info["public_key"],
        client_info["private_key"]
    )

    # Pass the configuration when building a new client instance.
    client = e3db.Client(config())

    # create record to be encypted and stored onto the Tozny database
    record_type = 'rps-move'
    data = {
        'player': args.name,
        'client_id': client_info["client_id"],
        'move': args.move
    }

    # create unencrypted metadata label specifying round number
    metadata = {
        'round-number': args.round
    }

    # check if there is already a move submitted for this round
    existing_record_query = Search().match(
        type='rps-move',
        plain={
            'round': args.round
        }
    )
    existing_record = client.search(existing_record_query)

    if len(existing_record) > 0:
        # there is already a move submitted for this round
        print('A move has already been submitted for round %d' % args.round)
    else:
        # try to write the record onto the Tozny database
        try:
            record = client.write(record_type, data, metadata)
            print('Successfully saved move for round %d' % args.round)
            print('Wrote record {0}'.format(record.meta.record_id))
        # handle any potential errors
        except Exception as e:
            print('Error:', e)
            exit(1)

        # try to share the records with the specified client ID
        try:
            client.share('rps-move', judge_client_id)
        # handle any potential errors
        except Exception as e:
            print('Error:', e)
            exit(1)


