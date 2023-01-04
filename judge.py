from e3db.types import Search
from utils import parse_args, load_client_credentials, create_client, share_record_type


def query_game_moves(client, round_number):
    """
    Query the Tozny database for game moves for the given round. Used in get_player_moves().

    Args:
        client (ToznyClient): a Tozny client instance
        round_number (str): the round number to query game moves for

    Returns:
        SearchResults: the search results containing the game moves

    Raises:
        Exception: if there is an error creating the game moves query or searching the database
    """
    try:
        game_moves_query = Search(include_data=True, include_all_writers=True).match(condition="AND", record_types=[
            "rps-move"], values=[round_number])
    except Exception as e:
        raise Exception("Error creating game moves query: {}".format(e))

    try:
        game_moves = client.search(game_moves_query)
    except Exception as e:
        raise Exception("Error searching for game moves: {}".format(e))

    return game_moves


def get_player_moves(client, round_number):
    """
    Retrieve the player moves for the given round.

    Args:
        client (ToznyClient): a Tozny client instance
        round_number (str): the round number to query game moves for

    Returns:
        tuple: the player 1 move data and player 2 move data as dictionaries

       Exception: if there are not exactly two game moves for the given round, 
                  or if the client IDs are the same
    """
    # query the game moves for the given round
    game_moves = query_game_moves(client, round_number)

    if len(game_moves) != 2:
        raise Exception(
            "Error: There should be exactly two game moves for round {}".format(round_number))

    # required keys in game move records
    required_keys = ['client_id', 'move', 'player']

    # Check if required keys are present in player move records
    for i in range(2):
        for key in required_keys:
            if key not in game_moves.records[i].data:
                raise KeyError(
                    "Error in game_moves data: Key '{}' not found in record {}.".format(key, i))

    # Check if client IDs are the same
    if game_moves.records[0].data['client_id'] == game_moves.records[1].data['client_id']:
        raise Exception('Error: Both players have the same client ID.')

    # return the player move data as a tuple
    return game_moves.records[0].data, game_moves.records[1].data


def determine_winner(p1_move_data, p2_move_data):
    """
    Determine the winner of a round of rock paper scissors.
    This function uses a dictionary to map each combination of moves to the winning move, 
    which allows for O(1) time complexity instead of going through a series of if-elif statements.

    Args:
        p1_move_data (dict): the move data for player 1, containing the player's name and move
        p2_move_data (dict): the move data for player 2, containing the player's name and move

    Returns:
        str: the name of the winning player or 'TIE' if the game is a draw
    """
    # create a dictionary that maps each combination of moves to the winning move
    winning_moves = {
        ('rock', 'scissors'): 'rock',
        ('rock', 'paper'): 'paper',
        ('scissors', 'rock'): 'rock',
        ('scissors', 'paper'): 'scissors',
        ('paper', 'rock'): 'paper',
        ('paper', 'scissors'): 'scissors'
    }

    # get the winning move for the moves played by player 1 and player 2
    winning_move = winning_moves.get(
        (p1_move_data['move'], p2_move_data['move']))

    # if there is a winning move, return the player who played it
    if winning_move == p1_move_data['move']:
        return p1_move_data['player']
    elif winning_move == p2_move_data['move']:
        return p2_move_data['player']
    # if there is no winning move, the game is a tie
    else:
        return 'TIE'


def write_round_result(client, round_number, winner):
    """
    Write round result record to the database.

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
    record_type = 'rps-result'
    data = {
        'winner': winner,
    }
    # create unencrypted metadata label specifying round number
    metadata = {
        'round-number': round_number
    }
    try:
        # write the record to the database
        return client.write(record_type, data, metadata)
    except Exception as e:
        raise RuntimeError("Error writing round result to database: %s" % e)


def main():

    # parse the command line arguments
    args = parse_args()

    # load the client credentials from the file
    client_info = load_client_credentials(
        args.tozny_client_credentials_filepath)

    # create a client instance
    client = create_client(client_info)

    # retrieve player moves for the given round
    player_1_move_data, player_2_move_data = get_player_moves(
        client, args.round)

    # determine winner using players' move data
    winner = determine_winner(player_1_move_data, player_2_move_data)

    # write the round result onto the Tozny database
    round_result = write_round_result(client, args.round, winner)
    print('Successfully saved result for round %s' % args.round)
    print('Wrote record %s' % round_result.meta.record_id)

    # share the game result record type with both players
    share_record_type(client, 'rps-result', player_1_move_data['client_id'])
    share_record_type(client, 'rps-result', player_2_move_data['client_id'])

    # Output round and winner information
    print("Round {} Judged! Winner: {}".format(args.round, winner))


if __name__ == '__main__':
    main()
