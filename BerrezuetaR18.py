from rdflib import *
import os
class ResumenISWC2019:
    g=Graph()
    
    def __init__(self, directory):
        self.directory=directory
        self.loadModels()
        self.setPrefix()
        self.getData()
        self.get_html()
        
    def loadModels(self):
        #Cargar los archivos ttl del directorio
        for raiz, directorios, archivos in os.walk(self.directory):
            for archivo in archivos:
                if archivo.endswith('.ttl'):
                    ruta_archivo = os.path.join(raiz, archivo)
                    g.parse(ruta_archivo, format='turtle')
    def setPrefix(self):
        #Prefijos
        conference = 'conference'
        self.CON = Namespace('https://w3id.org/scholarlydata/ontology/conference-ontology.owl#')
        dbo='dbo' 
        DBO = Namespace('http://dbpedia.org/ontology/')
        dbp='dbp' 
        DBP = Namespace('http://dbpedia.org/property/')
        dbr='dbr' 
        DBR = Namespace('http://dbpedia.org/resource/')
        purl='purl'
        PURL=Namespace('http://purl.org/dc/elements/1.1/')
        rdfs='rdfs'
        self.RDFs=Namespace('http://www.w3.org/2000/01/rdf-schema#')
        organization='org'
        ORG=Namespace('https://w3id.org/scholarlydata/organisation/')
        # Ejecutar una consulta SPARQL
        self.PREFIX = f"""
        PREFIX {conference}: <{self.CON}>
        PREFIX {purl}: <{PURL}>
        PREFIX {rdfs}: <{self.RDFs}>
        PREFIX {organization}: <{ORG}>
        PREFIX {dbo}: <{DBO}>
        PREFIX {dbp}: <{DBP}>
        """
    def getAutorList(self,articleiri):
        autores=[]
        authorlist=next(g.objects(URIRef(articleiri),self.CON.hasAuthorList),None)
        if authorlist is None:
            return ""
        item=next(g.objects(authorlist,self.CON.hasFirstItem),None)
        while item:
            content=next(g.objects(item,self.CON.hasContent),None)
            name=next(g.objects(content,self.RDFs.label),None)
            autores.append(name.value)
            item=next(g.objects(item,self.CON.next),None)
        str_autores=", ".join(autores[:-1])
        return str_autores + " y "+autores[-1]
        
    def short(self,track):
        if track == "in-Use":
            return "(EU)"
        elif track == "Research":
            return "(IN)"
        return "(RC)"
        
    def getData(self):
        q1=self.PREFIX + """
        SELECT DISTINCT ?pais ?articulo ?iriarticulo ?track 
        WHERE {
            ?p a conference:Track;
            conference:hasSubEvent ?a;
            rdfs:label ?track.
            ?a a conference:Talk;
            conference:isEventRelatedTo ?iriarticulo.
            ?iriarticulo rdfs:label ?articulo;
            purl:creator/conference:hasAffiliation/conference:withOrganisation/dbo:country/dbp:name ?pais.
            
            OPTIONAL {
                ?a a conference:Session;
                conference:hasSubEvent ?t.
                ?t a conference:Talk;
                conference:isEventRelatedTo ?iriarticulo.
                ?iriarticulo rdfs:label ?articulo;
                purl:creator/conference:hasAffiliation/conference:withOrganisation/dbo:country/dbp:name ?pais.
            
            }
            FILTER (?track = "In-Use" || ?track = "Research" || ?track = "Resource")
        }
        ORDER BY ?pais ?articulo
        """
        paises=dict([])
        results = g.query(q1)
        for row in results:
            track=self.short(row.track.value)
            autores=self.getAutorList(row.iriarticulo)
            titulo=row.articulo.value
            pais=row.pais.value
            texto=f"""{track} "{titulo}" por {autores}"""
            try:
                paises[pais].append(texto)
            except:
                paises[pais]=[texto]

        self.data=paises
        
    def get_html(self):

        elements=""
        for i in self.data.keys():
            elements=elements+f"<h2>{i}</h2><ul>"
            for j in self.data[i]:
                elements=elements+f"<li>{j}</li>"
            elements=elements+"</ul>"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pubicaciones ISWC 2019</title>
        </head>
        <body>
            <h1>ISWC es el principal foro internacional para la comunidad de datos enlazados y web
semántica. Esta página web enumera todas las publicaciones de tres
tópicos de la conferencia organizadas por país</h1>
            {elements}
        </body>
        </html>
        """
        with open("PubicacionesISWC2019.html", "w", encoding="utf-8") as file:
            file.write(html_content)

ResumenISWC2019("./Users/renatomacbook/Desktop/10mo Ciclo/Web Semantica/Practica 18")