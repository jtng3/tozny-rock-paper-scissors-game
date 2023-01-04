import json
from e3db.types import Search
from utils import parse_args_for_gameplay, load_client_credentials, create_client, share_record_type


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


def write_round_move(client, round_number, name, move, client_id):
    """
    Write a round move record to the database.

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


def main():

    # parse the command line arguments
    args = parse_args_for_gameplay()

    # use the hardcoded judge client ID if the optional argument was not provided
    with open('judge-client-id.json', 'r') as f:
        config = json.load(f)
    judge_client_id = args.judge_id or config['judge_client_id']

    # load the Tozny client credentials from the file
    client_info = load_client_credentials(
        args.tozny_client_credentials_filepath)

    # create a client instance
    client = create_client(client_info)

    # check if there is already a move submitted for this round
    existing_records = get_existing_records(client, args.round)
    if len(existing_records) > 0:
        # there is already a move submitted for this round
        raise RuntimeError(
            'A move has already been submitted for round %s' % args.round)

    # write the record onto the Tozny database
    record = write_round_move(client, args.round, args.name,
                              args.move, client_info["client_id"])
    print('Successfully saved move for round %s' % args.round)
    print('Wrote record %s' % record.meta.record_id)

    # share the records with the Judge
    share_record_type(client, 'rps-move', judge_client_id)


if __name__ == '__main__':
    main()
