"""Estilo da página (grimório): cores por categoria e CSS."""

PAGE_CSS = """
:root{ --ink:#cdd3e0; }
*{ box-sizing:border-box; }
body{
  margin:0; padding:0 0 90px; color:var(--ink);
  font-family:'Segoe UI',system-ui,sans-serif;
  background:radial-gradient(circle at 50% -8%, #1b2340, #0a0d18 70%);
  min-height:100vh;
}
header{
  position:sticky; top:0; z-index:5; display:flex; align-items:center; gap:14px;
  padding:14px 24px; border-bottom:1px solid #ffffff14;
  background:rgba(10,13,24,.72); backdrop-filter:blur(8px);
}
header h1{ margin:0; font-size:18px; font-weight:600; letter-spacing:.08em; }
header .sp{ flex:1; }
.btn{
  background:#ffffff10; border:1px solid #ffffff24; color:var(--ink);
  padding:7px 13px; border-radius:9px; cursor:pointer; font-size:13px;
  text-decoration:none; display:inline-block;
}
.btn:hover{ background:#ffffff20; }

.code{ max-width:1120px; margin:0 auto; padding:26px 30px; }
.line{
  display:flex; flex-wrap:wrap; align-items:center; gap:8px;
  min-height:30px; padding:5px 0; border-bottom:1px dashed #ffffff0a;
}
.line.blank{ min-height:14px; border-bottom:none; }

.glyph{ display:inline-flex; flex-direction:column; align-items:center; position:relative; }
.glyph svg.seal-svg{ width:64px; height:64px; }
.glyph svg.mark{ width:36px; height:36px; }
.glyph svg.orb{ width:48px; height:48px; }

.cartouche{
  display:inline-flex; align-items:center; gap:1px; padding:3px 9px;
  border-radius:11px; background:#ffffff08; border:1px solid #ffffff16;
}
.cartouche svg.rune{ height:26px; width:auto; }
.qmark{ opacity:.6; font-size:15px; padding:0 3px; }

/* cores por categoria (os SVGs usam currentColor) */
.keyword{ color:#e8c468; }
.builtin{ color:#5fd0c5; }
.operator{ color:#aab3c5; }
.identifier{ color:#e9d9b8; }
.number{ color:#d99873; }
.string{ color:#9bd17a; }
.comment{ color:#6b7488; }
.dunder{ color:#c79be8; }
.private{ color:#d8c59a; }
.special{ color:#86e0d0; }
.summon{ color:#e6a3c7; }      /* funções/classes definidas pelo usuário */
.cartouche.dunder{ border-color:#c79be84d; }
.glyph svg.specialmark{ width:34px; height:34px; }

/* botão "mostrar texto": revela o token original embaixo de cada glifo */
body.show-text .glyph::after{
  content:attr(data-text); margin-top:3px; font-size:10px; opacity:.6;
  font-family:ui-monospace,Consolas,monospace; color:#aeb6c7; white-space:nowrap;
}

/* folha de referência */
.section{ max-width:1120px; margin:0 auto; padding:16px 30px; }
.section h2{
  font-size:13px; letter-spacing:.14em; text-transform:uppercase; color:#8a93a8;
  border-bottom:1px solid #ffffff14; padding-bottom:8px; margin:18px 0 0;
}
.grid{ display:grid; grid-template-columns:repeat(auto-fill,minmax(98px,1fr)); gap:14px; margin-top:16px; }
.cell{
  display:flex; flex-direction:column; align-items:center; gap:7px; padding:12px 8px;
  border:1px solid #ffffff12; border-radius:13px; background:#ffffff06;
}
.cell .g svg{ width:64px; height:64px; }
.cell .g svg.rune{ width:36px; height:50px; }
.cell .lbl{ font-family:ui-monospace,Consolas,monospace; font-size:12px; color:#aeb6c7; }
.intro{ max-width:1120px; margin:0 auto; padding:8px 30px 0; color:#9098ad; font-size:14px; }
"""
