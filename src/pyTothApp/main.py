from toth.core import application, benchmark, collection, constants, formats, genome, io
from toth.steps import prepare, alignment

if __name__ == "__main__":
    
    #creating the instance of the config file
    url = 'http://fstakoviak.bol.ucla.edu/bioinformatics/config/server.ini'
    
    config = application.Config(url)

    #step 1 - Prepare files
    ref_file = prepare.ReferenceFile(config)
    read_file = prepare.ReadFile(config)

    ref_file.split()
    read_file.split()

    ref_file.kmerizer(4, 2)
    ref_file.kmerizer(10, 2)

    #step 2 - Pre Align
    pre_align = alignment.PreAlignment(config)

    read_list = collection.ReadList(config)
    n_lines = read_list.number_lines()

    pre_align.run(0, n_lines)

    #step 3 - Pileup / Consensus
