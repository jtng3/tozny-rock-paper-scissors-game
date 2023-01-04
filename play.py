import argparse
import json
from e3db.types import Search
from utils import valid_round, valid_move, valid_file_path, valid_client_id, load_client_credentials, create_client


def parse_args():
    """
    Parse the command line arguments.

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


def get_existing_records(client, round_number):
    """
    Get any records that have already been submitted for the specified round number.

    Args:
        client: A e3db.Client instance.
        round_number: The round number to search for.

    Returns:
        A list of e3db.Record objects.

    Raises:
        RuntimeError: If there was an error creating the query or searching for records.
    """
    try:
        # create a search query to find records with the specified round number
        query = Search().match(condition="AND", record_types=[
            "rps-move"], values=[round_number])
    except Exception as e:
        raise RuntimeError("Error creating existing records query: %s" % e)
    try:
        # search for records using the created query
        return client.search(query)
    except Exception as e:
        raise RuntimeError(
            "Error searching for existing records for round %s: %s" % (round_number, e))


def write_record(client, round_number, name, move, client_id):
    """
    Write a record to the database.

    Args:
        client: A e3db.Client instance.
        round_number: The round number of the record.
        name: The name of the player.
        move: The move made by the player.
        client_id: The client ID of the player.

    Returns:
        The written e3db.Record object.

    Raises:
        RuntimeError: If there was an error writing the record to the database.
    """
    record_type = 'rps-move'
    data = {
        'player': name,
        'client_id': client_id,
        'move': move
    }
    # create unencrypted metadata label specifying round number
    metadata = {
        'round-number': round_number
    }
    try:
        # write the record to the database
        return client.write(record_type, data, metadata)
    except Exception as e:
        raise RuntimeError("Error writing record to database: %s" % e)


def share_record(client, record_type, client_id):
    """
    Share a record with the specified client.

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


def main():

    # parse the command line arguments
    args = parse_args()

    # use the hardcoded judge client ID if the optional argument was not provided
    with open('judge-client-id.json', 'r') as f:
        config = json.load(f)
    judge_client_id = args.judge_id or config['judge_client_id']

    # load the Tozny client credentials from the file
    client_info = load_client_credentials(
        args.tozny_client_credentials_filepath)

    # pass credientials into the configuration constructor
    # create a client instance
    client = create_client(client_info)

    # check if there is already a move submitted for this round
    existing_records = get_existing_records(client, args.round)
    if len(existing_records) > 0:
        # there is already a move submitted for this round
        raise RuntimeError(
            'A move has already been submitted for round %s' % args.round)

    # write the record onto the Tozny database
    record = write_record(client, args.round, args.name,
                          args.move, client_info["client_id"])
    print('Successfully saved move for round %s' % args.round)
    print('Wrote record %s' % record.meta.record_id)

    # share the records with the specified client ID
    share_record(client, 'rps-move', judge_client_id)


if __name__ == '__main__':
    main()
