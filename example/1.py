import requests

url = 'http://localhost:8000'

def start(user_key, problem_id, count):
    uri = url + '/start/' + user_key + '/' + str(problem_id) + '/' + str(count)
    return requests.post(uri).json()

def onCall(token):
    uri = url + "/oncalls"
    return requests.get(uri, headers={'X-Auth-Token':token}).json()

def action(token, commmands):
    uri = url + "/action"
    return requests.post(uri, headers={'X-Auth-Token':token}, json={"commands": commmands}).json

def create_command(e_id, command, c_id):
    return {"elevator_id": e_id, "command": command, "call_ids": c_id}

def create_command_noCall(e_id, command):
    return {"elevator_id": e_id, "command": command}    

def is_open(calls, passengers, floor, b_status):
    for call in calls:
        if call['start'] == floor:
            if is_top or is_bottom:
                return True
            else:
                if b_status == 'up' and call['end'] - call['start'] > 0:
                    return True
                elif b_status == 'down' and call['end'] - call['start'] < 0:
                    return True
    for passenger in passengers:
        if passenger['end'] == floor:
            return True
    return False

def is_top(calls, passengers, floor):
    top = -1
    for call in calls:
        top = max(top, call['start'])
    for passenger in passengers:
        top = max(top, passenger['end'])

    if floor >= top:
        return True
    else:
        return False

def is_bottom(calls, passengers, floor):
    bottom = 100000
    for call in calls:
        bottom = min(bottom, call['start'])
    for passenger in passengers:
        bottom = min(bottom, passenger['end'])

    if floor <= bottom:
        return True
    else:
        return False

def simulator():
    user = 'tester'
    problem = 0
    count = 1

    token = start(user, problem, count)
    token = token["token"]

    before_status = ['stop', 'stop', 'stop', 'stop']
    while True:
        res = onCall(token)

        if res['is_end']:
            break

        elevators = res['elevators']
        calls = res['calls']
        
        commands = []
        for elevator in elevators:
            e_id = elevator['id']
            floor = elevator['floor']
            passengers = elevator['passengers']
            status = elevator['status']

            if status == "STOPPED":
                if is_open(calls, passengers, floor, before_status[e_id]):
                    commands.append(create_command_noCall(e_id, 'OPEN'))
                elif is_top(calls, passengers, floor) or before_status[e_id] == 'down':
                    commands.append(create_command_noCall(e_id, 'DOWN'))
                    before_status[e_id] = 'down'
                elif is_bottom(calls, passengers, floor) or before_status[e_id] == 'up':
                    commands.append(create_command_noCall(e_id, 'UP'))
                    before_status[e_id] = 'up'
                else:
                    commands.append(create_command_noCall(e_id, 'STOP'))
                    before_status[e_id] = 'stop'

            elif status == "UPWARD":
                if is_open(calls, passengers, floor, before_status[e_id]):
                    commands.append(create_command_noCall(e_id, 'STOP'))
                    before_status[e_id] = 'stop'
                else:
                    commands.append(create_command_noCall(e_id, 'UP'))
                    before_status[e_id] = 'up'

            elif status == "DOWNWARD":
                if is_open(calls, passengers, floor, before_status[e_id]):
                    commands.append(create_command_noCall(e_id, 'STOP'))
                    before_status[e_id] = 'stop'
                else:
                    commands.append(create_command_noCall(e_id, 'DOWN'))
                    before_status[e_id] = 'down'

            elif status == "OPENED":
                enters = []
                exits = []
                for call in calls:
                    if call['start'] == floor:
                        enters.append(call['id'])
                for passenger in passengers:
                    if passenger['end'] == floor:
                        exits.append(passenger['id'])

                if enters:
                    commands.append(create_command(e_id, 'ENTER', enters))
                elif exits:
                    commands.append(create_command(e_id, 'EXIT', exits))
                else:
                    commands.append(create_command_noCall(e_id, 'CLOSE'))

        action(token, commands)
        

if __name__ == "__main__":
    simulator()
