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
    
    outfile = outfile + '.html'

    net.save_graph(outfile)




# Function to create a Pyvis network graph
def create_custom_pyvis_network(relationships, output_file):
    net = Network(height='600px', width='100%', directed=True)

    threat_keywords = ["attack", "threat", "security", "breach", "vulnerable", "malware", "hack", "exploit", "ransomware", "phishing", "virus", "fraud", "scam", "compromise", "infiltrate","crime", "terror", "extremist", "protest", "riot", "violence", "radical", "smuggle", "trafficking", "illegal", "attack", "threat", "breach", "infiltrate", "smuggling", "unrest", "militant", "militia", "disorder", "gang"]

    added_nodes = set()
    for subject, verb, obj in relationships:
        if subject != obj:  # Ensure no self-referential relationships
            if subject not in added_nodes:
                color = "red" if any(keyword in subject.lower() for keyword in threat_keywords) else "lightblue"
                net.add_node(subject, title=subject, color=color)
                added_nodes.add(subject)
            if obj not in added_nodes:
                color = "red" if any(keyword in obj.lower() for keyword in threat_keywords) else "lightblue"
                net.add_node(obj, title=obj, color=color)
                added_nodes.add(obj)
            edge_color = "red" if any(keyword in verb.lower() for keyword in threat_keywords) else "blue"
            net.add_edge(subject, obj, label=verb, font=dict(size=20, color=edge_color))


    # Hotfix for issue with / in URI which prevents us from saving graph
    output_file = output_file.split("/")[-1]
    outfile = output_file + '.html'
    
    # Save the graph as an HTML file
    net.save_graph(outfile)



            


def main():

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
    
    create_custom_pyvis_network([
    ("Al-Shabaab", "Somalia", "poses a persistent threat to"),
    ("Al-Shabaab", "civilians and officials", "targets"),
    ("Al-Shabaab", "U.N. helicopter", "captures"),
    ("Al-Shabaab", "six passengers", "takes hostage"),
    ("Al-Shabaab", "Emirati and Bahraini security officers", "kills in attack"),
    ("Mohamud’s administration", "Al-Shabaab", "launches a large-scale offensive against"),
    ("Al-Shabaab", "territory and soldiers", "lose in initial phase of offensive"),
    ("Somali defense minister", "second phase of offensive", "delays due to logistical and weather challenges")
], """https://www.nytimes.com/2024/02/27/world/africa/somalia-ethiopia-al-shabab-conflict.html""")



if __name__ == "__main__":

    main()