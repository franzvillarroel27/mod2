// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

contract SubastaFlashCompleta {
    // Estructura para registrar cada oferta individual
    struct OfertaIndividual {
        uint monto;
        uint timestamp;
        bool reembolsada;
    }

    // Variables de estado
    address public immutable owner;
    address public mejorOferente;
    uint public mejorOferta;
    uint public inicio;
    uint public duracionInicial = 5 minutes;
    uint public duracionActual;
    bool public finalizada;

    // Registro completo de ofertas
    mapping(address => OfertaIndividual[]) public historialOfertas;
    mapping(address => uint) public saldosParticipantes;
    address[] public participantes;

    // Eventos mejorados
    event NuevaOferta(address indexed oferente, uint monto, uint nuevoTiempoFinal);
    event SubastaExtendida(uint tiempoAnterior, uint nuevoTiempoFinal);
    event SubastaFinalizada(address ganador, uint monto);
    event FondosRetirados(address indexed to, uint amount);
    event ReembolsoParcial(address indexed oferente, uint monto);

    constructor() {
        owner = msg.sender;
        inicio = block.timestamp;
        duracionActual = duracionInicial;
    }

    modifier subastaActiva() {
        require(!finalizada, "Subasta finalizada");
        require(block.timestamp <= inicio + duracionActual, "Tiempo terminado");
        _;
    }

    modifier soloOwner() {
        require(msg.sender == owner, "No eres el owner");
        _;
    }

    function ofertar() external payable subastaActiva {
        require(msg.value > 0, "Debes enviar ETH");

        uint total = saldosParticipantes[msg.sender] + msg.value;
        uint minimoRequerido = mejorOferta + (mejorOferta * 5) / 100;

        if (mejorOferta > 0) {
            require(total >= minimoRequerido, "La oferta debe superar en al menos 5%");
        }

        // Extender la subasta en 5 minutos por cada nueva oferta
        uint tiempoAnterior = inicio + duracionActual;
        duracionActual += 10 minutes;
        emit SubastaExtendida(tiempoAnterior, inicio + duracionActual);

        // Registrar oferta individual
        historialOfertas[msg.sender].push(OfertaIndividual({
            monto: msg.value,
            timestamp: block.timestamp,
            reembolsada: false
        }));

        saldosParticipantes[msg.sender] = total;
        mejorOferente = msg.sender;
        mejorOferta = total;

        // Registrar participante si es nuevo
        if (historialOfertas[msg.sender].length == 1) {
            participantes.push(msg.sender);
        }

        emit NuevaOferta(msg.sender, msg.value, inicio + duracionActual);
    }

    // FUNCIONALIDAD NUEVA: Reembolso parcial durante subasta
    function retirarExcedente(uint monto) external subastaActiva {
        require(monto > 0, "Monto debe ser positivo");
        uint excedente = saldosParticipantes[msg.sender];
        
        // Si es el mejor oferente, solo puede retirar el excedente sobre su mejor oferta
        if (msg.sender == mejorOferente) {
            excedente -= mejorOferta;
        }
        
        require(excedente >= monto, "Fondos insuficientes");
        
        saldosParticipantes[msg.sender] -= monto;
        payable(msg.sender).transfer(monto);
        
        emit ReembolsoParcial(msg.sender, monto);
    }

    function finalizar() external soloOwner {
        require(!finalizada, "Ya finalizo");
        require(block.timestamp >= inicio + duracionActual, "Aun no termina");

        finalizada = true;
        emit SubastaFinalizada(mejorOferente, mejorOferta);
    }

    function retirar() external {
        require(finalizada, "Subasta no finalizada");
        require(msg.sender != mejorOferente, "Ganador no puede retirar");

        uint deposito = saldosParticipantes[msg.sender];
        require(deposito > 0, "Nada para retirar");

        uint comision = (deposito * 2) / 100;
        uint reembolso = deposito - comision;

        saldosParticipantes[msg.sender] = 0;
        payable(msg.sender).transfer(reembolso);
        emit FondosRetirados(msg.sender, reembolso);
    }

    function retirarFondos() external soloOwner {
        require(finalizada, "Subasta no finalizada");
        require(address(this).balance > 0, "Sin balance disponible");

        uint monto = mejorOferta;
        uint comision = (monto * 2) / 100;
        uint neto = monto - comision;

        // Transferir comisión al owner
        payable(owner).transfer(neto);
        emit FondosRetirados(owner, neto);
    }

    // FUNCIONALIDAD NUEVA: Listado completo de ofertas
    function obtenerTodasOfertas() external view returns (
        address[] memory,
        uint[] memory,
        uint[] memory,
        bool[] memory
    ) {
        uint totalOfertas;
        for (uint i = 0; i < participantes.length; i++) {
            totalOfertas += historialOfertas[participantes[i]].length;
        }

        address[] memory direcciones = new address[](totalOfertas);
        uint[] memory montos = new uint[](totalOfertas);
        uint[] memory timestamps = new uint[](totalOfertas);
        bool[] memory estados = new bool[](totalOfertas);

        uint contador;
        for (uint i = 0; i < participantes.length; i++) {
            for (uint j = 0; j < historialOfertas[participantes[i]].length; j++) {
                direcciones[contador] = participantes[i];
                montos[contador] = historialOfertas[participantes[i]][j].monto;
                timestamps[contador] = historialOfertas[participantes[i]][j].timestamp;
                estados[contador] = historialOfertas[participantes[i]][j].reembolsada;
                contador++;
            }
        }

        return (direcciones, montos, timestamps, estados);
    }

    function tiempoRestante() external view returns (uint) {
        if (block.timestamp >= inicio + duracionActual || finalizada) {
            return 0;
        }
        return (inicio + duracionActual) - block.timestamp;
    }

    function verBalance() external view returns (uint) {
        return address(this).balance;
    }

    function obtenerDuracion() external view returns (uint inicial, uint actual) {
        return (duracionInicial, duracionActual);
    }
}





