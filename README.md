📜 README - Contrato de Subasta Flash con Extensiones Dinámicas
https://img.shields.io/badge/Solidity-0.8.26-informational?logo=solidity
https://img.shields.io/badge/License-MIT-blue

📌 Descripción
Contrato inteligente para subastas descentralizadas con:

Extensiones automáticas de tiempo (+10 minutos por oferta)

Reembolsos parciales durante la subasta

Registro completo de historial de ofertas

Comisión del 2% para el administrador

🚀 Características Principales
✅ Extensiones dinámicas: Cada oferta añade 10 minutos al tiempo de subasta

✅ Reembolsos parciales: Retira fondos que no sean tu oferta líder

✅ Transparencia total: Consulta todas las ofertas históricas

✅ Comisiones automáticas: 2% para el owner al finalizar

✅ Seguro: Protecciones contra reentrada y validaciones robustas

📦 Instalación
Clona el repositorio:

bash
git clone https://github.com/tu-usuario/subasta-flash.git
cd subasta-flash
Instala dependencias:

bash
npm install
🛠 Uso Básico
Despliegue
solidity
// Usando Hardhat/Foundry
const SubastaFlash = await ethers.getContractFactory("SubastaFlashCompleta");
const subasta = await SubastaFlash.deploy();
Interacción
javascript
// Ofertar
await subasta.ofertar({ value: ethers.utils.parseEther("1") });

// Retirar excedente
await subasta.retirarExcedente(ethers.utils.parseEther("0.5"));

// Finalizar subasta (solo owner)
await subasta.finalizar();
📖 Documentación de Funciones
Funciones Principales
Función	Descripción
ofertar()	Envía ETH para participar (extiende subasta)
retirarExcedente(uint monto)	Retira fondos no comprometidos
finalizar()	Finaliza la subasta (solo owner)
retirar()	Reclama fondos después de finalizar
Consultas
Función	Descripción
obtenerTodasOfertas()	Devuelve historial completo
tiempoRestante()	Muestra segundos hasta el final
verBalance()	Muestra ETH en el contrato
🔍 Estructura de Datos
solidity
struct OfertaIndividual {
    uint monto;
    uint timestamp; 
    bool reembolsada;
}

// Almacenamiento
mapping(address => OfertaIndividual[]) public historialOfertas;
mapping(address => uint) public saldosParticipantes;
🌐 Eventos
Evento	Descripción
NuevaOferta	Emitido al recibir oferta
SubastaExtendida	Cuando se añade tiempo
ReembolsoParcial	Al retirar fondos durante subasta
⚠️ Consideraciones de Seguridad
Solo el owner puede finalizar la subasta

Comisión del 2% aplicada a reembolsos

Validaciones:

Ofertas deben ser ≥5% mayores

No se aceptan ofertas después del tiempo final

📝 Ejemplo de Flujo
Despliegue: Subasta inicia con 5 minutos

Oferta 1:

Envía 1 ETH

Tiempo se extiende a 15 minutos

Oferta 2:

Debe ser ≥1.05 ETH

Tiempo se extiende a 25 minutos

Finalización:

Owner llama finalizar()

Participantes reclaman fondos

📜 Licencia
MIT License - Ver LICENSE para detalles.
