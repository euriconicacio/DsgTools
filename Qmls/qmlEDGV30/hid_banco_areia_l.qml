<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'><qgis version="2.6.0-Brighton" minimumScale="1" maximumScale="1" simplifyDrawingHints="0" minLabelScale="0" maxLabelScale="1e+08" simplifyDrawingTol="1" simplifyMaxScale="1" hasScaleBasedVisibilityFlag="0" simplifyLocal="1" scaleBasedLabelVisibilityFlag="0"> 
  <edittypes> 
     <edittype widgetv2type="TextEdit" name="OGC_FID"> 
      <widgetv2config IsMultiline="0" fieldEditable="0" UseHtml="0" labelOnTop="0"/> 
    </edittype> 
    <edittype widgetv2type="TextEdit" name="id"> 
      <widgetv2config IsMultiline="0" fieldEditable="0" UseHtml="0" labelOnTop="0"/> 
    </edittype>
    <edittype widgetv2type="ValueMap" name="tipobanco">
      <widgetv2config fieldEditable="1" labelOnTop="0">
        <value key="Fluvial" value="2"/>
        <value key="Cordão arenoso" value="3"/>
        <value key="Marítimo" value="4"/>
        <value key="Lacustre" value="12"/>
      </widgetv2config>
    </edittype> 
    <edittype widgetv2type="ValueMap" name="geometriaaproximada">
      <widgetv2config fieldEditable="1" labelOnTop="0">
        <value key="Não" value="0"/>
        <value key="Sim" value="1"/>
      </widgetv2config>
    </edittype> 
    <edittype widgetv2type="ValueMap" name="situacaoemagua">
      <widgetv2config fieldEditable="1" labelOnTop="0">
        <value key="Emerso" value="5"/>
        <value key="Cobre e descobre" value="6"/>
        <value key="Submerso" value="7"/>
        <value key="Desconhecido" value="95"/>
      </widgetv2config>
    </edittype> 
    <edittype widgetv2type="ValueMap" name="materialpredominante">
      <widgetv2config fieldEditable="1" labelOnTop="0">
        <value key="Misto" value="98"/>
        <value key="Rocha" value="13"/>
        <value key="Areia" value="14"/>
        <value key="Areia fina" value="15"/>
        <value key="Lama" value="16"/>
        <value key="Concha" value="17"/>
        <value key="Argila" value="18"/>
        <value key="Lodo" value="19"/>
        <value key="Cascalho" value="20"/>
        <value key="Seixo" value="21"/>
        <value key="Pedra" value="23"/>
        <value key="Coral" value="24"/>
        <value key="Desconhecido" value="95"/>
        <value key="Não aplicável" value="97"/>
        <value key="Outros" value="99"/>
      </widgetv2config>
    </edittype> 
  </edittypes>
</qgis>