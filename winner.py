import argparse
from e3db.types import Search
from utils import valid_round, valid_file_path, load_client_credentials, create_client


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


def get_game_result(client, round_number):
    """
    Get the game result for the given round number.

    Args:
        client (e3db.Client): the E3DB client instance.
        round_number (int): the round number.

    Returns:
        e3db.Record: the game result record.

    Raises:
        RuntimeError: if there is no game result for the given round number
                      or if there is more than one game result for the given round number.
    """
    # try querying the Tozny database for game result
    try:
        query = Search(include_data=True, include_all_writers=True).match(condition="AND", record_types=[
            "rps-result"], values=[round_number])
    except Exception as e:
        raise RuntimeError("Error creating game results query: %s" % e)
    try:
        game_results = client.search(query)
    except Exception as e:
        raise RuntimeError("Error searching for game results: %s" % e)

    if len(game_results) == 0:
        raise RuntimeError(
            'Error: There is no game result for round %s' % round_number)
    elif len(game_results) > 1:
        # there are more than one game result for this round
        raise RuntimeError(
            'Error: There appears to be more than one game result for round %s' % round_number)
    else:
        return game_results.records[0]


def main():
    # parse the command line arguments
    args = parse_args()

    # load the client credentials from the file
    client_info = load_client_credentials(
        args.tozny_client_credentials_filepath)

    # create a client instance
    client = create_client(client_info)

    # get the game result for the given round
    try:
        game_result = get_game_result(client, args.round)
    except RuntimeError as e:
        print(e)
        exit(1)

    # print the game result
    print('Game result is:')
    print(game_result.data)


if __name__ == '__main__':
    main()
