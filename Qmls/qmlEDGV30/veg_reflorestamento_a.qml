<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'><qgis version="2.6.0-Brighton" minimumScale="1" maximumScale="1" simplifyDrawingHints="0" minLabelScale="0" maxLabelScale="1e+08" simplifyDrawingTol="1" simplifyMaxScale="1" hasScaleBasedVisibilityFlag="0" simplifyLocal="1" scaleBasedLabelVisibilityFlag="0"> 
  <edittypes> 
     <edittype widgetv2type="TextEdit" name="OGC_FID"> 
      <widgetv2config IsMultiline="0" fieldEditable="0" UseHtml="0" labelOnTop="0"/> 
    </edittype> 
    <edittype widgetv2type="TextEdit" name="id"> 
      <widgetv2config IsMultiline="0" fieldEditable="0" UseHtml="0" labelOnTop="0"/> 
    </edittype>
    <edittype widgetv2type="TextEdit" name="id_area_verde"> 
      <widgetv2config IsMultiline="0" fieldEditable="0" UseHtml="0" labelOnTop="0"/> 
    </edittype>
    <edittype widgetv2type="ValueMap" name="geometriaaproximada">
      <widgetv2config fieldEditable="1" labelOnTop="0">
        <value key="Não" value="0"/>
        <value key="Sim" value="1"/>
      </widgetv2config>
    </edittype> 
    <edittype widgetv2type="ValueMap" name="tipoveg">
      <widgetv2config fieldEditable="1" labelOnTop="0">
        <value key="Vegetação cultivada" value="1"/>
      </widgetv2config>
    </edittype> 
    <edittype widgetv2type="ValueMap" name="classificacaoporte">
      <widgetv2config fieldEditable="1" labelOnTop="0">
        <value key="Rasteira" value="2"/>
        <value key="Herbácea" value="3"/>
        <value key="Arbórea" value="4"/>
        <value key="Arbustiva" value="5"/>
        <value key="Desconhecida" value="95"/>
        <value key="Mista" value="97"/>
      </widgetv2config>
    </edittype> 
    <edittype widgetv2type="ValueMap" name="densidade">
      <widgetv2config fieldEditable="1" labelOnTop="0">
        <value key="Alta" value="1"/>
        <value key="Baixa" value="2"/>
        <value key="Desconhecida" value="95"/>
      </widgetv2config>
    </edittype> 
    <edittype widgetv2type="ValueMap" name="tipolavoura">
      <widgetv2config fieldEditable="1" labelOnTop="0">
        <value key="Anual" value="20"/>
        <value key="Perene" value="21"/>
        <value key="Semi-perene" value="22"/>
        <value key="Desconhecido" value="95"/>
      </widgetv2config>
    </edittype> 
    <edittype widgetv2type="ValueMap" name="finalidade">
      <widgetv2config fieldEditable="1" labelOnTop="0">
        <value key="Ornamental" value="2"/>
        <value key="Exploração econômica" value="3"/>
        <value key="Subsistência" value="4"/>
        <value key="Conservação ambiental" value="5"/>
        <value key="Desconhecida" value="95"/>
        <value key="Outros" value="99"/>
      </widgetv2config>
    </edittype> 
    <edittype widgetv2type="ValueMap" name="cultivopredominante">
      <widgetv2config fieldEditable="1" labelOnTop="0">
        <value key="Eucalipto" value="22"/>
        <value key="Acácia" value="23"/>
        <value key="Algaroba" value="24"/>
        <value key="Pinus" value="25"/>
        <value key="Araucária" value="29"/>
        <value key="Carnaúba" value="30"/>
        <value key="Juta" value="34"/>
        <value key="Não identificado" value="96"/>
        <value key="Rami" value="76"/>
        <value key="Outros" value="99"/>
      </widgetv2config>
    </edittype> 
  </edittypes>
</qgis>