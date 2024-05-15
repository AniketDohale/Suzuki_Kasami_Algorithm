##################################################################################################################

sn -> Sequence number of a Request 
i -> Site ID

##################################################################################################################

Token -> ( Sites that Requests for Critical Section )

RN[i] -> [ No. of Sites, Store the Information of all the other Sites ]

LN[i] -> [ Array is Updated by Site which holds the Token ]

Token Queue = [ Store the Pending Requests of Sites ]

##################################################################################################################

- A Request is not Accepted / Outdated Request
if 
    RN_i[j] >= sn

- A Request is Accepted and Replied with a Token
if  
    RN_i[j] < sn

##################################################################################################################


Start with Node 1:
Node 1 has the token initially, so it can read and write to the shared file.

Test read from Node 1:

GET http://127.0.0.1:5000/read_shared_file

Test write from Node 1:

POST http://127.0.0.1:5000/write_shared_file with body {"message": "Node 1 was here"}

Request the Token from Other Nodes:

If Node 2 or Node 3 wants the token, they need to request it.

For Node 2:
POST http://127.0.0.1:5001/request_token with body {"target_node": "127.0.0.1:5000"}

For Node 3:

POST http://127.0.0.1:5002/request_token with body {"target_node": "127.0.0.1:5000"}

Pass the Token:
Node 1 can pass the token to the next node in the queue.

To release the token from Node 1:

POST http://127.0.0.1:5000/release_token

The token will be passed to the node at the top of the queue (Node 2 or Node 3).

Operations with the Token:

If Node 2 gets the token, it can now read and write:

GET http://127.0.0.1:5001/read_shared_file
POST http://127.0.0.1:5001/write_shared_file with body {"message": "Node 2 was here"}
