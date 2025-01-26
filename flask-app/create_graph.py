from pyvis.network import Network
import spacynlp


def generate_graph(relationships):
    net = Network(height='600px', width='100%', directed=False)

    for relationship in relationships:
        if len(relationship) == 2:
            net.add_node(relationship[0], title=relationship[0])
            net.add_node(relationship[1], title=relationship[1])

            net.add_edge(relationship[0], relationship[1])
        elif len(relationship) == 3:
            net.add_node(relationship[0], title=relationship[0])
            net.add_node(relationship[1], title=relationship[1])

            net.add_edge(relationship[0], relationship[2], label=relationship[1])
        else:
            print("ERROR!")
    
    net.save_graph("entity_relationship.html")

            


def main(text):

    generate_graph(spacynlp.spacynlp_process(text))



if __name__ == "__main__":

    sample_text = """Myanmar's military regime is now facing a harder time in getting access to funding globally.

Singapore's United Overseas Bank (UOB) is cutting off ties with banks in Myanmar from Friday (Sep 1), a move that is in step with international sanctions targeting Myanmar's banking industry.

The bank will restrict all incoming and outgoing payments to and from Myanmar accounts. It will also put curbs on Visa and Mastercard transactions from Myanmar.

With this latest move, the Singapore lender is effectively severing ties with its Myanmar counterparts. 

CNA has reached out to the bank but UOB said it cannot comment on client relationships."""


    main(sample_text)