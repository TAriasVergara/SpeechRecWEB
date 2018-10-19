function goBack() {
    window.history.back();
}

function logval() {
	if (LogVal=="True")
	{
		document.getElementById("vallog").text="\u26DD  Logout";
		document.getElementById("vallog").setAttribute("href","/logout")
	}
	else{
		document.getElementById("vallog").value="\u26BF Login";
		document.getElementById("vallog").setAttribute("href","/login")
	}

}


function setbval(obj,val)
{
	var temp = document.getElementById(obj);
	temp.value = val;
}

/* 
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Change state of button after POST
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
*/
function recButton(elemID,rec_cont,msgelem)
{	 
	var RecVal = document.getElementById(elemID);
	if (RecVal.innerHTML=="START")
	{
		document.getElementById(elemID).value = "True";
	}
	else
	{
		$(rec_cont).addClass("hidden");
		document.getElementById(elemID).value = "False";
		document.getElementById(msgelem).innerHTML = "Daten speichern Warten Sie mal";
		
	}
	
}

function recTimer(elemID)
{
	var seconds = 0;
	var minutes = 0;
	// Update the count up every 1 second
	var x = setInterval(function() 
	{
		seconds++
		if (seconds==60)
		{
			seconds=0;
			minutes++;
		}
		
		document.getElementById(elemID).innerHTML = minutes.toString() + 'm: ' + seconds.toString() + 's ';
	
	}, 1000);
}
/* 
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Generate an speaker ID for Healthy controls REGISTER.HTML
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
*/
function generate_spkID(itemID) {
	var code = "H";
	var num = Math.floor(Math.random() * 100000000);
	num = num.toString()
	var res = code.concat(num);
	document.getElementById(itemID).value=res;
}
/* 
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Toggle between adding and removing the "responsive" class 
to topnav when the user clicks on the icon
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
*/
function toggle_menu(barid) {
    var x = document.getElementById(barid);
    if (x.className === "topnav") {
		x.className += " responsive";		
		document.getElementById("icon").text="\u26DD";
    } else {        
		x.className = "topnav";		
		document.getElementById("icon").text="\u2630";
    }
} 

//Limpiar entradas
function clear_inputs(classcont)
{
	var c = document.getElementById(classcont).querySelectorAll('*');//Obtener todos los elementos de una clase
	for (i = 0; i < c.length; i++) 
	{
		var temp = c[i].nodeName;//Verificar que sea entrada
		if (temp.localeCompare('INPUT')==0)
		{
			
			var elem = c[i].type//Verificar el tipo de entrada
			if ((elem.localeCompare('radio')==0)||(elem.localeCompare('checkbox')==0))
			{
				c[i].checked=false;
			}	
			if ((elem.localeCompare('number')==0)||(elem.localeCompare('text')==0)||(elem.localeCompare('date')==0))
			{
				c[i].value='';
			}
			c[i].required=false;
		}
    }
}

// Activar contenedores (clases ocultas)
function setCont(containerID) 
{
	$(containerID).removeClass("hidden");
	enableinputs(containerID);
}
//Borrar respuestas de contenedores y ocultar
function ResetCont(containerID)
{
	clear_inputs($(containerID).attr('id'));
	$(containerID).addClass("hidden");	
}

//Activar/desactivar elementos especificos
function setElem(opt,textInput)
{	
	var obj = document.getElementById(opt)
	var input=document.getElementById(textInput); 
	if(obj.checked)
	{ 
		input.disabled = false; 
		input.focus();
		input.required = true;
	}
	else
	{
		input.value='';
		input.disabled=true;
		input.required = false;
	}
}

function enableinputs(classcont)
{
	var c = document.getElementById($(classcont).attr('id')).querySelectorAll('*');//Obtener todos los elementos de una clase
	for (i = 0; i < c.length; i++) 
	{
		var temp = c[i].nodeName;//Verificar que sea entrada
		if (temp.localeCompare('INPUT')==0)
		{
			c[i].required = true;
		}
    }
}

/* 
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
DYNAMIC PROGRESSION BAR
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
*/
/* Progression bar 1: The bar is filled automatically */
function move(button_id) {
	var bt_id = button_id
	var elem = document.getElementById("Bar");   
	var width = 0;
	var id = setInterval(frame, 65);
	function frame() {
	if (width == 100) {
		clearInterval(id);
	} else {
		width++; 
		elem.style.width = width + '%'; 
		if (width == 100) {
			document.getElementById(bt_id).disabled = false;
	}
	}
	}
}
/* Progression bar 2: The bar is filled "manually"*/
function progressB(width) 
{
	var elem = document.getElementById("Bar");
	width++;
	elem.style.width = width + '%'; 
}


/*-------------------------------------------------------------------------
---------------------------------------------------------------------------
---------------------------------------------------------------------------
---------------------------------------------------------------------------
---------------------------------------------------------------------------*/
//preguntas.html
//Cargar respuestas tipo radio
function set_radios(x,val)
{
	var radio = x[i].value;
	if (radio.localeCompare(val)==0)
	{	
		var temp = x[i].id

		document.getElementById(x[i].id).checked = true;//MARCAR respuesta
		if (temp.search('_hab')!=-1)//Para disparar eventos que habilitan otras opciones
		{
			$(document.getElementById(x[i].id)).click();			
		}
	}
}
//marcar respuestas tipo checkbox
function set_checkbox(x,val)
{
	for( j = 0; j < val.length; j++ ) 
	{
		var check = x.value;
		if (check.localeCompare(val[j])==0)
		{	
			var temp = x.id	
			if (temp.search('_hab')!=-1)//Para disparar eventos que habilitan otras opciones
			{
				$(document.getElementById(x.id)).click();			
			}
			document.getElementById(x.id).checked = true;
		}
	}
}
//Marcar preguntas contestadas
function set_rtas()
{
	for(var key in Rtas)
	{
		if (key.localeCompare('ID')!=0)
		{
			var x = document.getElementsByName(key);
			var val = Rtas[key];			
			for( i = 0; i < x.length; i++ ) 
			{				
				var elem = x[i].type	
				if (elem.localeCompare('radio')==0)
				{
					set_radios(x,val);
				}
				if (elem.localeCompare('checkbox')==0)
				{
					set_checkbox(x[i],val);
				}
				if ((elem.localeCompare('number')==0)||(elem.localeCompare('text')==0)||(elem.localeCompare('date')==0))
				{
					document.getElementById(x[i].id).value = val;
				}
			}
		}
	}
	
}

/* 
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Hidden Metadata table in CI_speech_data_html 
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
*/
function set_metadata(containerID)
{
	if (meta_flag=="on")
	{
		$(containerID).removeClass("hidden");
	}
}
