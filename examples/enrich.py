import pandas as pd
import gseapy as gp
from gseapy import dotplot


class AutoEnrich:
    default_DBs = ['GO_Biological_Process_2021', 'GO_Biological_Process_2023', 'GO_Biological_Process_2025',
                   'GO_Cellular_Component_2021', 'GO_Cellular_Component_2023', 'GO_Cellular_Component_2025',
                   'GO_Molecular_Function_2021', 'GO_Molecular_Function_2023', 'GO_Molecular_Function_2025',
                   'GTEx_Aging_Signatures_2021',
                   'KEGG_2019_Human', 'KEGG_2021_Human', 'KEGG_2026',
                   'Reactome_2022', 'Reactome_Pathways_2024']
    def __init__(self, organism='Human', gene_identifier='ensembl_gene_id', attributes=None):
        self._available_models = ['best', 'interpretable', 'aggressivefs', 'univariate']
        self.set_options(organism=organism, gene_identifier=gene_identifier, attributes=attributes)
        self.geneset = None

    def get_JAD_geneset(self, client, AID, models=None):
        self.client = client
        if models is None:
            self.models = self._available_models
        res = self.client.get_analysis_result(AID)
        gs = []
        for mdi in self.models:
            if mdi  in res['models'].keys():
                for sigi in res['models'][mdi]['signatures']:
                    gs.extend(sigi)
        self.geneset = list(set(gs))
        return self.geneset

    def set_options(self, organism='Human', gene_identifier='ensembl_gene_id',
                    attributes=None):
        if attributes is None:
            attributes = ['ensembl_gene_id', 'external_gene_name', 'entrezgene_id', 'hgnc_symbol',
                          'description', 'gene_biotype']
        self.attributes = attributes
        self.organism = organism
        self.gene_identifier = gene_identifier

    def get_gene_info(self, geneset=None):
        bm = gp.Biomart()
        if self.organism == 'Human':
            dataset = 'hsapiens_gene_ensembl'
        if geneset is None:
            if self.geneset is None:
                raise ValueError('Please specify the geneset, either by list, or retreive from JAD (`get_JAD_geneset(client, AID)`)')
            else:
                geneset = self.geneset
        filters = {self.gene_identifier: geneset}
        info = bm.query(dataset='hsapiens_gene_ensembl',
                        attributes=self.attributes,
                        filters=filters)
        return info

    def get_DB_index(self):
        dbs = pd.Series(gp.get_library_name(organism=self.organism))
        dbs.name = 'DBs'
        return dbs

    def enrich(self, background=None, include_default_DBs=True, other_DBs=None,
               out_dir='./enrich_results.csv', plot=True,
               p_value=0.05, adjust=True, oddR=None, cscore=None):
        DBs = []
        if include_default_DBs:
            DBs.extend(AutoEnrich.default_DBs)
        if other_DBs is not None:
            DBs.extend(other_DBs)
        if self.organism == 'Human':
            organism = 'human'
        if background is None:
            if self.organism == 'Human':
                background = 'hsapiens_gene_ensembl'

        AEA = gp.enrich(gene_list=self.geneset,
                        gene_sets=DBs,
                        background=background,
                        outdir=out_dir, no_plot=not plot,
                        verbose=True)
        self.gsea_results = AEA
        return AEA.results

    def barplot(self, gsea_results=None, p_value=1, adjust=True, oddR=None, cscore=None):
        pass

    def dotplot(self, gsea_results=None, p_value=1, adjust=True, oddR=None, cscore=None,
                column="Adjusted P-value",
                x='Gene_set',  # set x axis, so you could do a multi-sample/library comparsion
                size=10,
                top_term=5,
                figsize=(3, 5),
                title="",
                xticklabels_rot=45,  # rotate xtick labels
                show_ring=True,  # set to False to remove outer ring
                marker='o'):
        if gsea_results is None:
            gsea_results = self.gsea_results.results

        ax = dotplot(gsea_results,
                     column=column, x=x,
                     size=size, top_term=top_term,
                     figsize=figsize, title=title, xticklabels_rot=xticklabels_rot,
                     show_ring=show_ring, marker=marker)
        return ax




