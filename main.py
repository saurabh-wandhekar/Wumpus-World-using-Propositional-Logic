#!/usr/bin/env python3
from Agent import * # See the Agent.py file
from pysat.solvers import Glucose3
from itertools import combinations

def Room_Number(loc):  # Function to find room_number for current location , ex : (1,1) is room 1, (4,4) is room 16
	return 4*(loc[1]-1) + loc[0]

def AdjacentRooms(loc):   # Function to find valid adjacent rooms
	x = loc[0]
	y = loc[1]
	moves = [[x,y+1],[x+1,y],[x-1,y],[x,y-1]]
	adjRooms = [z for z in moves if z[0]>0 and z[0]<5 and z[1]>0 and z[1]<5]
	return adjRooms

def main():
	ag = Agent()
	kb = [[16]]     # We know (4,4) is safe. Note that [x] is added implying x is safe and [-x] is added if x is unsafe
	visited = [['None', 0] for i in range(1,18)]  # visited list of the form [percept, number of times visited]
	path = []
	dont_visit = None

	while(ag.FindCurrentLocation() != [4,4]):     

		loc = ag.FindCurrentLocation()

		path.append(loc)    # Path taken from source to destination

		curr_room_no = Room_Number(loc)
	
		adjRooms = AdjacentRooms(loc)

		percept = ag.PerceiveCurrentLocation()

		visited[curr_room_no][1] += 1      
		visited[curr_room_no][0] += percept

		k = [curr_room_no]
		if k not in kb:
			kb.append(k)

		if(percept == '=0'):  # add to kb [curr_room] as well as [adjacent_room] for all adjacent rooms. 
			for room in adjRooms:
				room_no = Room_Number(room)
				k = [room_no]
				if k not in kb:
					kb.append(k)

		elif(percept == '=1'):  # (-a V -b V -c) and (a V b) and (b v c) and (c v a) if a,b,c are adjacent rooms
		                        # (-a V -b V -c V -d) and (a V b) and (b v c) and (c v a) and (a V d) and (b v d) and (c v d) if a,b,c,d are adjacent rooms
			temp = []
			for room in adjRooms:
				room_no = Room_Number(room)
				temp.append(-room_no)
			if temp not in kb:
				kb.append(temp)

			pairs = [[-a, -b] for idx, a in enumerate(temp) for b in temp[idx + 1:] if [-a, -b] not in kb]
			kb = kb + pairs

		elif(percept == '>1'):  # (-a V -b) and (-b v -c) and (-c v -a) if a,b,c are adjacent rooms
		                        # (-a V -b V -c) and (-a V -b V -d) and (-b V -c V -d) and (-a V -c V -d) if a,b,c,d are adjacent rooms
			temp = []
			for room in adjRooms:
				room_no = Room_Number(room)
				temp.append(-room_no)

			if(len(temp) == 4):
				comb = combinations(temp, 3)
			elif(len(temp) == 3):
				comb = combinations(temp, 2)

			m = list(comb)
			for i in m:
				if list(i) not in kb:
					kb.append(list(i))


		g = Glucose3()
		for x in kb:     # adding clauses in knowledge base to glucose3 object
			g.add_clause(x)

		can_move = []   # all adjacent rooms which are safe

		for i in adjRooms:
			room_no = Room_Number(i)
			if(g.solve(assumptions = [-room_no])==False):   # kb and ~a derives box clause which means a is safe
				can_move.append(room_no)    

		if(can_move == []):  # no possible move
			break

		def myFunc(e):            # sort can_move according to number of times visited   
			return visited[e][1]
       
		can_move.sort(key = myFunc)

		unvisited = [i for i in can_move if visited[i][1] == 0]  # all adjacent safe rooms which are unvisited

		unvisited.sort(reverse = True)   # sorting to ensure shortest path, i.e Up and Right preferred over Down and Left

		flag = 0
		if(unvisited != []):

			i = unvisited[0]

			if(i == curr_room_no + 1):
				ag.TakeAction('Right')
				
			elif(i == curr_room_no + 4):
				ag.TakeAction('Up')

			elif(i == curr_room_no - 1):
				ag.TakeAction('Left')
				dont_visit = curr_room_no

			elif(i == curr_room_no - 4):
				ag.TakeAction('Down')
				dont_visit = curr_room_no
			
			flag = 1

		if flag == 1:   # If action is taken then control goes to the start of the loop, else the following code will be executed
			continue
        
        # Now we will check in visited rooms which are visited least

		i = can_move[0]
		if(i == curr_room_no + 1):
			ag.TakeAction('Right')

		elif(i == curr_room_no + 4):
			ag.TakeAction('Up')
			
		elif(i == curr_room_no - 1):
			ag.TakeAction('Left')
			dont_visit = curr_room_no

		elif(i == curr_room_no - 4):
			ag.TakeAction('Down')
			dont_visit = curr_room_no
			
		flag = 1

		if flag == 0:
			break

	if(ag.FindCurrentLocation() != [4,4]):
		print("Path doesn't exist")

	else:
		ag.TakeAction('Right')
		print("Path found and Agent exits the Wumpus World")
		print("Path followed :" , end = ' ')
		for i in path:
			print(i, "-->" , end = ' ')
		print([4,4])
		#print("Path Length = ", len(path) + 1)


if __name__=='__main__':
	main()
