import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


queue = QueueFrontier()
already_checked_nodes = set()

def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    # source = person_id_for_name(input("Name: "))
    source = person_id_for_name("Tom Cruise")
    if source is None:
        sys.exit("Person not found.")
    # target = person_id_for_name(input("Name: "))
    target = person_id_for_name("Cary Elwes")
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")

def shortest_path(source: int, target: int):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    movie_id_for_actor_id = neighbors_for_person(source)
    source_node = Node(state= source, parent= None, action=None)
    create_nodes_and_add_to_que(parent=source_node, movie_id_for_actor_id=movie_id_for_actor_id)
    match_target_node = False
    while match_target_node == False:
        match_target_node = check_for_target_and_delete_old_nodes(queue.frontier, target)
        if queue.empty():
            print("Empty queue")
            return None
    result_path = construct_result_path(match_target_node, source)
    if result_path != []:
        return result_path
    else:
        print("No Connection")
        return None

            
def create_nodes_and_add_to_que(parent: Node, movie_id_for_actor_id: set) -> None:
    """
    Creates Nodes and checks if the nodes were already checked before
    Adds unchecked nodes to queue
    """
    for movie in movie_id_for_actor_id:
        movie_id = movie[0]
        actor_id = movie[1]
        node = Node(state=actor_id, parent=parent, action=movie_id)
        if any(checked_node.state == actor_id and checked_node.movie == movie_id for checked_node in already_checked_nodes):
            print("ALREADY CHECKED")
        else:
            queue.add(node)


def check_for_target_and_delete_old_nodes(nodes_list: list, target: int):
    """
    Checks for target node
    Returns node if it is the target
    If the node is not the target
    it creates new nodes from it,
    then removes it and adds the new nodes to que
    Returns False if target was not found
    """
    for node in nodes_list:
        if node.state == target:
            print(f'NODE: {node.state}')
            return node
        else:
            already_checked_nodes.add(node)
            movie_id_for_actor_id = neighbors_for_person(node.state)
            create_nodes_and_add_to_que(node, movie_id_for_actor_id)
            queue.remove()
    return False

def construct_result_path(match_target_node: Node, source: int) -> list:
    """
    Recusivly goes through the parent of the node 
    and adds the parent to a list 
    till the root node which has no parent
    Returns the list
    """
    result_path = []
    while 1:
        print(f'RESULT PATH: {result_path}')
        if match_target_node.state != source:
            result_path.append((match_target_node.action, match_target_node.state))
            match_target_node = match_target_node.parent
        else:
            break
    return result_path

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
