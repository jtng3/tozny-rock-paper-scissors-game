import argparse
import json
import e3db
from e3db.types import Search
from utils import valid_round, valid_file_path


def main():
    # create an argument parser
    parser = argparse.ArgumentParser()

    # add the round number and client credentials filepath arguments
    parser.add_argument('round', type=valid_round,
                        help='the round number')
    parser.add_argument('tozny_client_credentials_filepath', type=valid_file_path,
                        help='the file path to the player\'s Tozny client credentials')

    # parse the command line arguments
    args = parser.parse_args()

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


    # try querying the Tozny database for game result
    try:
        game_results_query = Search(include_data=True, include_all_writers=True).match(condition="AND", record_types=[
        "rps-result"], values=[args.round])
    except Exception as e:
        print("Error creating game result query:", e)
        exit(1)

    try:
        game_results = client.search(game_results_query)
    except Exception as e:
        print("Error searching for game result:", e)
        exit(1)


    if len(game_results) == 0:
        print('Error: There is no game result for round %s' % args.round)
    elif len(game_results) > 1:
        # there is already a move submitted for this round
        print('Error: There appears to be more than one game result for round %s' % args.round)
    else:
        print('Game result is: ')
        print(game_results.records[0].data)





