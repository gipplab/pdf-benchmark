from sciwing.models.neural_parscit import NeuralParscit
from sciwing.models.citation_intent_clf import CitationIntentClassification

# instantiate an object
neural_parscit = NeuralParscit()
#citation_intent_clf = CitationIntentClassification()

# predict on a citation
neural_parscit.predict_for_text("#Koehn, P., Och, F. J., and Marcu, D. (2003). Statistical phrase-based translation. In Proceedings of the 2003 Conference of the North American Chapter of the ACL, pages 48–54, Edmonton, Canada.")
#citation_intent_clf.predict_for_text("Koehn, P., Och, F. J., and Marcu, D. (2003). Statistical phrase-based translation. In Proceedings of the 2003 Conference of the North American Chapter of the ACL, pages 48–54, Edmonton, Canada.")
# if you have a file of citations with one citation per line
#neural_parscit.predict_for_file("/path/to/filename")

#Koehn, P., Och, F. J., and Marcu, D. (2003). Statistical phrase-based translation. In Proceedings of the 2003 Conference of the North American Chapter of the ACL, pages 48–54, Edmonton, Canada.