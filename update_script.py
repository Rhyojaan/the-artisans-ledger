from pathlib import Path
import re

path = Path("script.js")
js = path.read_text(encoding="utf-8")

replacement = r'''function openLedger(){
  const gate=document.getElementById("tomeGate");
  if(!gate)return;

  gate.classList.add("openingLedger");

  setTimeout(()=>{
    gate.style.display="none";

    if(!archive.profiles.length){
      setup.style.display="block";
      app.style.display="none";
      return;
    }

    render();
    const first=document.querySelector(".tab");
    if(first)showTab("advisor",first);
  },1450);
}

render();
'''

js = re.sub(
    r'function openLedger\(\)[\s\S]*?render\(\);\s*$',
    replacement,
    js
)

path.write_text(js, encoding="utf-8")
print("script.js updated")
