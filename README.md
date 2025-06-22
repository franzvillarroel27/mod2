📜 README - Contrato de Subasta Flash

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

🏗️ Estructura del Código
El contrato está organizado en 5 secciones principales:

1.- Definiciones iniciales:

Versión de Solidity (pragma)

Licencia (MIT)

Estructura de datos OfertaIndividual

2.- Variables de estado:

solidity
```bash
    address public immutable owner;
    address public mejorOferente;
    uint public mejorOferta;
    uint public inicio;
    uint public duracionInicial = 5 minutes;
    uint public duracionActual;
    bool public finalizada;
```
3.- Sistemas de almacenamiento:

solidity
```bash

    mapping(address => OfertaIndividual[]) public historialOfertas;
    mapping(address => uint) public saldosParticipantes;
    address[] public participantes;
```
Eventos:

solidity
```bash

    event NuevaOferta(address indexed oferente, uint monto, uint nuevoTiempoFinal);
    event SubastaExtendida(uint tiempoAnterior, uint nuevoTiempoFinal);
    event SubastaFinalizada(address ganador, uint monto);
    event FondosRetirados(address indexed to, uint amount);
    event ReembolsoParcial(address indexed oferente, uint monto);
```
5.- Funciones (clasificadas por propósito):

Modificadores (subastaActiva, soloOwner)

Operaciones principales (ofertar, retirarExcedente)

Finalización (finalizar, retirar, retirarFondos)

Consultas (obtenerTodasOfertas, tiempoRestante, verBalance)

🎯 Funcionalidades Clave
1. Mecanismo de Ofertas
solidity
```bash

    function ofertar() external payable subastaActiva {
        require(msg.value > 0, "Debes enviar ETH");
        uint total = saldosParticipantes[msg.sender] + msg.value;
        uint minimoRequerido = mejorOferta + (mejorOferta * 5) / 100;
        
        if (mejorOferta > 0) {
            require(total >= minimoRequerido, "Oferta debe ser ≥5% mayor");
        }
        
        // Extensión de tiempo (+10 min)
        duracionActual += 10 minutes;
        
        // Registro histórico
        historialOfertas[msg.sender].push(OfertaIndividual({
            monto: msg.value,
            timestamp: block.timestamp,
            reembolsada: false
        }));
        
        // Actualización de estado
        saldosParticipantes[msg.sender] = total;
        mejorOferente = msg.sender;
        mejorOferta = total;
    }
```
2. Sistema de Extensiones
Lógica: Cada oferta exitosa añade 10 minutos a duracionActual

Ejemplo:

Subasta inicia con 5 min

Oferta 1 (t=0): duración = 15 min

Oferta 2 (t=10 min): duración = 25 min

3. Reembolsos Parciales
solidity
```bash

    function retirarExcedente(uint monto) external subastaActiva {
        uint excedente = saldosParticipantes[msg.sender];
        
        if (msg.sender == mejorOferente) {
            excedente -= mejorOferta; // Solo permite retirar el excedente
        }
        
        require(excedente >= monto, "Fondos insuficientes");
        saldosParticipantes[msg.sender] -= monto;
        payable(msg.sender).transfer(monto);
    }
```

4. Finalización y Comisiones
solidity
```bash

    function retirarFondos() external soloOwner {
        require(finalizada, "Subasta no finalizada");
        uint monto = mejorOferta;
        uint comision = (monto * 2) / 100;
        uint neto = monto - comision;
        payable(owner).transfer(neto); // Owner recibe el 98%
    }
```

🔄 Flujo de Datos
Diagram

```bash

    graph TD
        A[Oferta] --> B{Validación}
        B -->|Éxito| C[Extender tiempo]
        C --> D[Registrar en historial]
        D --> E[Actualizar mejor oferta]
        E --> F[Emitir eventos]
        B -->|Fallo| G[Revertir]

```

📊 Estructura de Almacenamiento
Variable	Tipo	Descripción
historialOfertas	mapping(address → OfertaIndividual[])	Todas las ofertas por dirección
saldosParticipantes	mapping(address → uint)	Balance total por participante
participantes	address[]	Lista de todos los oferentes
⚙️ Funciones de Consulta
1.- obtenerTodasOfertas():

Devuelve 4 arrays paralelos:

Direcciones

Montos

Timestamps

Estados de reembolso

2.- tiempoRestante():

solidity
```bash

return (inicio + duracionActual) - block.timestamp;
```

3.- verBalance():

solidity
```bash

return address(this).balance;
```

🛡️ Modelo de Seguridad
Patrón Checks-Effects-Interactions:

Todas las funciones validan (require) antes de actuar

Estados se actualizan antes de transferencias ETH

Protección contra reentrada:

Uso de transfer() (limita gas a 2300 unidades)

Acceso restringido:

finalizar() y retirarFondos() solo para owner





