const historie = document.getElementById('historie')
historie.addEventListener('change', (event) => {
  var myClasses = document.querySelectorAll('.noshow');
  for (i=0; i < myClasses.length; i++) {
    if (document.getElementById('historie').checked) {
      myClasses[i].style.display="table-row";}
    else {
      myClasses[i].style.display="none";
      }
    }
  }
)
