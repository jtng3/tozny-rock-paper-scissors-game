import argparse
import json
import e3db
from e3db.types import Search
from utils import valid_round, valid_move, valid_file_path, valid_client_id


def main():
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
    args = parser.parse_args()

    # use the hardcoded judge client ID if the optional argument was not provided
    judge_client_id = args.judge_id or 'hardcoded_judge_client_id'

    # try to load the Tozny client credentials from the file
    try:
        with open(args.tozny_client_credentials_filepath, 'r') as f:
            client_info = json.load(f)
    # handle any potential errors
    except (IOError, json.JSONDecodeError) as e:
        print('Error loading client credentials from file:', e)
        exit(1)

    # pass credientials into the configuration constructor
    config = e3db.Config(
        client_info["client_id"],
        client_info["api_key_id"],
        client_info["api_secret"],
        client_info["public_key"],
        client_info["private_key"]
    )

    # pass the configuration when building a new client instance.
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
    try:
        existing_records_query = Search().match(condition="AND", record_types=[
        "rps-move"], values=[args.round])
    except Exception as e:
        print("Error creating existing records query:", e)
        exit(1)

    try:
        existing_records = client.search(existing_records_query)
    except Exception as e:
        print("Error searching for existing record:", e)
        exit(1)

    if len(existing_records) > 0:
        # there is already a move submitted for this round
        print('Error: A move has already been submitted for round %s' % args.round)
        exit(1)
    else:
        # try to write the record onto the Tozny database
        try:
            record = client.write(record_type, data, metadata)
            print('Successfully saved move for round %s' % args.round)
            print('Wrote record {0}'.format(record.meta.record_id))
        # handle any potential errors
        except Exception as e:
            print('Error writing record to database:', e)
            exit(1)

    # try to share the records with the specified client ID
    try:
        client.share('rps-move', judge_client_id)
    # handle any potential errors
    except Exception as e:
        print('Error sharing record with Judge:', e)
        exit(1)


if __name__ == '__main__':
    main()
