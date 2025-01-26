from pyvis.network import Network
import os

def generate_graph(relationships, outfile):
    net = Network(height='600px', width='100%', directed=True)

    for relationship in relationships:
        if len(relationship) == 2:
            net.add_node(relationship[0], title=relationship[0])
            net.add_node(relationship[1], title=relationship[1])

            net.add_edge(relationship[0], relationship[1])
        elif len(relationship) == 3:
            net.add_node(relationship[0], title=relationship[0])
            net.add_node(relationship[1], title=relationship[1])

            net.add_edge(relationship[0], relationship[1], label=relationship[2])
        else:
            print("ERROR!")
    
    outfile = "graphs/" + outfile + '.html'

    net.save_graph(outfile)

            


def main(text):

    generate_graph([
    ("Russia", "North Korea", "provides military cargo and support"),
    ("South Korea", "Russia", "imposes sanctions and restrictions"),
    ("Maria Zakharova", "South Korea", "issues diplomatic warnings to"),
    ("Russian vessels", "North Korea", "transport military cargo to"),
    ("Russian Foreign Ministry", "South Korea", "condemns actions of"),
    ("South Korea", "Russian organizations", "places sanctions on"),
    ("Russia", "Russian citizens", "allows involvement with North Korean programs"),
    ("Seoul", "Pyongyang", "attempts to restrict military development of")
], "test")



if __name__ == "__main__":

    sample_text = """Myanmar's military regime is now facing a harder time in getting access to funding globally.

Singapore's United Overseas Bank (UOB) is cutting off ties with banks in Myanmar from Friday (Sep 1), a move that is in step with international sanctions targeting Myanmar's banking industry.

The bank will restrict all incoming and outgoing payments to and from Myanmar accounts. It will also put curbs on Visa and Mastercard transactions from Myanmar.

With this latest move, the Singapore lender is effectively severing ties with its Myanmar counterparts. 

CNA has reached out to the bank but UOB said it cannot comment on client relationships."""


    main(sample_text)