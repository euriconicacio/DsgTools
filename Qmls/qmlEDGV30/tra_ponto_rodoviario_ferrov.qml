<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'><qgis version="2.6.0-Brighton" minimumScale="1" maximumScale="1" simplifyDrawingHints="0" minLabelScale="0" maxLabelScale="1e+08" simplifyDrawingTol="1" simplifyMaxScale="1" hasScaleBasedVisibilityFlag="0" simplifyLocal="1" scaleBasedLabelVisibilityFlag="0"> 
  <edittypes> 
     <edittype widgetv2type="TextEdit" name="OGC_FID"> 
      <widgetv2config IsMultiline="0" fieldEditable="0" UseHtml="0" labelOnTop="0"/> 
    </edittype> 
    <edittype widgetv2type="TextEdit" name="id"> 
      <widgetv2config IsMultiline="0" fieldEditable="0" UseHtml="0" labelOnTop="0"/> 
    </edittype>
    <edittype widgetv2type="ValueMap" name="relacionado">
      <widgetv2config fieldEditable="1" labelOnTop="0">
        <value key="Passagem elevada ou viaduto" value="3"/>
        <value key="Ponte" value="15"/>
        <value key="Travessia" value="24"/>
        <value key="Contato com localidade" value="26"/>
        <value key="Edificação rodoviária" value="27"/>
        <value key="Entrocamento" value="28"/>
        <value key="Galeria ou bueiro" value="29"/>
        <value key="Início/fim de trecho" value="30"/>
        <value key="Mudança de UF" value="31"/>
        <value key="Mudança de administração" value="32"/>
        <value key="Mudança de número de faixas" value="34"/>
        <value key="Mudança de revestimento" value="35"/>
        <value key="Mudança de tipo de rodovia" value="36"/>
        <value key="Mudança do número de pistas" value="38"/>
        <value key="Desconhecido" value="95"/>
      </widgetv2config>
    </edittype> 
    <edittype widgetv2type="ValueMap" name="geometriaaproximada">
      <widgetv2config fieldEditable="1" labelOnTop="0">
        <value key="Não" value="0"/>
        <value key="Sim" value="1"/>
      </widgetv2config>
    </edittype> 
  </edittypes>
</qgis>