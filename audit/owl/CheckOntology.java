import java.io.File;
import java.util.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.profiles.OWL2DLProfile;
import org.semanticweb.owlapi.reasoner.OWLReasoner;
import org.semanticweb.HermiT.Reasoner;

public class CheckOntology {
    public static void main(String[] args) throws Exception {
        OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
        OWLOntology ontology = manager.loadOntologyFromOntologyDocument(new File(args[0]));
        Map<String,Object> out = new LinkedHashMap<>();
        out.put("file", new File(args[0]).getName());
        out.put("axioms", ontology.getAxiomCount());
        out.put("equivalent_class_axioms", ontology.getAxiomCount(AxiomType.EQUIVALENT_CLASSES));
        out.put("object_property_assertions", ontology.getAxiomCount(AxiomType.OBJECT_PROPERTY_ASSERTION));
        List<String> violations = new ArrayList<>();
        new OWL2DLProfile().checkOntology(ontology).getViolations().forEach(v -> violations.add(v.toString()));
        Collections.sort(violations);
        out.put("dl_profile_violations", violations);
        List<String> definitions = new ArrayList<>();
        ontology.getAxioms(AxiomType.EQUIVALENT_CLASSES).forEach(a -> definitions.add(a.toString()));
        Collections.sort(definitions); out.put("definitions", definitions);
        try {
            OWLReasoner reasoner = new Reasoner.ReasonerFactory().createReasoner(ontology);
            out.put("consistent", reasoner.isConsistent());
            OWLDataFactory df = manager.getOWLDataFactory();
            OWLClass c = df.getOWLClass(IRI.create("https://example.org/clinical-kg/PhenotypeAnnotatedConcept"));
            OWLNamedIndividual t = df.getOWLNamedIndividual(IRI.create("http://purl.obolibrary.org/obo/MONDO_0005148"));
            out.put("t2dm_annotation_class_entailed", reasoner.isEntailed(df.getOWLClassAssertionAxiom(c,t)));
            OWLObjectProperty inverse = df.getOWLObjectProperty(IRI.create("https://example.org/clinical-kg/phenotypeOf"));
            OWLNamedIndividual hp = df.getOWLNamedIndividual(IRI.create("http://purl.obolibrary.org/obo/HP_0000855"));
            out.put("inverse_entailed", reasoner.isEntailed(df.getOWLObjectPropertyAssertionAxiom(inverse,hp,t)));
            reasoner.dispose();
            OWLObjectProperty positive = df.getOWLObjectProperty(IRI.create("https://example.org/clinical-kg/hasPhenotype"));
            Set<OWLAxiom> removed = new HashSet<>();
            ontology.getAxioms(AxiomType.OBJECT_PROPERTY_ASSERTION).forEach(a -> {
                if (a.getProperty().equals(positive)) removed.add(a);
            });
            manager.removeAxioms(ontology, removed);
            OWLReasoner ablated = new Reasoner.ReasonerFactory().createReasoner(ontology);
            out.put("removed_positive_assertions", removed.size());
            out.put("classification_after_positive_ablation", ablated.isEntailed(df.getOWLClassAssertionAxiom(c,t)));
            out.put("inverse_after_positive_ablation", ablated.isEntailed(df.getOWLObjectPropertyAssertionAxiom(inverse,hp,t)));
            ablated.dispose();
        } catch (Exception ex) { out.put("reasoner_error", ex.toString()); }
        System.out.println("RESULT_JSON=" + new ObjectMapper().writeValueAsString(out));
    }
}
