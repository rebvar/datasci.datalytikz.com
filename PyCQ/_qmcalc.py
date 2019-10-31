
output_endl = True;
output_filename = True;
indentation_list = True;

#// Process and print the metrics of stdin
from ._CMetricsCalculator import CMetricsCalculator

def process_metrics(filename):
    cm = CMetricsCalculator()

    out = ''

    if (indentation_list):
        cm.enable_indentation_list();
    cm.calculate_metrics();
    out+=cm.get_metrics()
    if (output_filename):
        out+='\t' + filename
    if (output_endl):
        out+='\n'
    print (out)

#/* Calculate and print C metrics for the standard input */
#int
def main(*args, **kwargs):
    pass
    #if (!argv[optind]) {
    #    process_metrics("-");
    #    exit(EXIT_SUCCESS);
    #}

    #// Read from file, if specified
    #while (argv[optind]) {
    #    in.open(argv[optind], std::ifstream::in);
    #    if (!in.good()) {
    #        std::cerr << "Unable to open " << argv[optind] <<
    #            ": " << strerror(errno) << std::endl;
    #        exit(EXIT_FAILURE);
    #    }
    #    std::cin.rdbuf(in.rdbuf());
    #    process_metrics(argv[optind]);
    #    in.close();
    #    optind++;
    #}

    #exit(EXIT_SUCCESS);
