from collections import defaultdict

import attr
from pathlib import Path
from pylexibank import Concept, Language, FormSpec
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.util import progressbar

from clldutils.misc import slug


@attr.s
class CustomConcept(Concept):
    Number = attr.ib(default=None)


class Dataset(BaseDataset):
    id = "felekesemitic"
    dir = Path(__file__).parent
    concept_class = CustomConcept

    form_spec = FormSpec(separators=",")

    def cmd_makecldf(self, args):
        languages = args.writer.add_languages(lookup_factory="Name")
        args.writer.add_sources()
        concepts = args.writer.add_concepts(
            id_factory=lambda x: x.id.split("-")[-1] + "_" + slug(x.english),
            lookup_factory=lambda concept: concept.english
            )

        cogs, maxcog = {}, 0
        data = self.raw_dir.read_csv("data.tsv", delimiter="\t")
        for row in progressbar(data):
            if row[1] == "English":
                current_concepts = row[2:]
            elif row[1] in languages:
                for concept, word in zip(current_concepts, row[2:]):
                    if word[-2].isdigit():
                        form = word[:-2]
                        cogid = word[-2:]
                    elif word[-1].isdigit():
                        form = word[:-1]
                        cogid = word[-1]
                    else:
                        form = word
                        cogid = '?'
                    if concept+'-'+cogid not in cogs:
                        cogs[concept+'-'+cogid] = maxcog+1
                        maxcog += 1
                    cognacy = cogs[concept+'-'+cogid]
                    lex = args.writer.add_form(
                            Parameter_ID=concepts[concept],
                            Language_ID=languages[row[1]],
                            Value=word,
                            Form=form,
                            Cognacy=cognacy,
                            Source='Feleke2021'
                            )
                    args.writer.add_cognate(
                            lexeme=lex,
                            Cognateset_ID=cognacy,
                            Source='Feleke2021'
                            )

