import React, { useState } from 'react';

interface Courses {
  curso_id: number;
  nombre: string;
  costo: number;
}

interface ModalProps {
  carrito: Courses[];
  cedulaUsuario: number;
  onPago: (pago: string) => void;
  onCerrar: () => void;
  error: string;
}

const ModalInscripcion: React.FC<ModalProps> = ({ 
  carrito, 
  cedulaUsuario, 
  onPago, 
  onCerrar, 
  error 
}) => {
  const [metodoPago, setMetodoPago] = useState('');
  const [datosTarjeta, setDatosTarjeta] = useState({
    numero: '',
    vencimiento: '',
    cvv: ''
  });

  const total = carrito.reduce((sum, curso) => sum + curso.costo, 0);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!metodoPago) {
      alert('Seleccione un método de pago');
      return;
    }
    onPago(metodoPago);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-black p-6 rounded-lg w-96 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">Proceso de Pago</h2>
        
        <div className="mb-6">
          <h3 className="font-semibold text-lg mb-2">Resumen de Compra</h3>
          <div className="space-y-2 mb-3">
            {carrito.map((curso) => (
              <div key={curso.curso_id} className="flex justify-between">
                <span>{curso.nombre}</span>
                <span>{curso.costo.toLocaleString()} Bs</span>
              </div>
            ))}
          </div>
          <div className="border-t pt-2 font-bold">
            <div className="flex justify-between">
              <span>Total:</span>
              <span>{total.toLocaleString()} Bs</span>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block mb-2 bg-black font-medium">Método de Pago</label>
            <select
              value={metodoPago}
              onChange={(e) => setMetodoPago(e.target.value)}
              className="w-full p-2 border rounded-md"
              required
            >
              <option value="">Seleccionar...</option>
              <option value="tarjeta">Tarjeta de Crédito/Débito</option>
              <option value="transferencia">Transferencia Bancaria</option>
              <option value="efectivo">Pago en Efectivo</option>
            </select>
          </div>

          {metodoPago === 'tarjeta' && (
            <div className="space-y-3 mb-4">
              <div>
                <label className="block mb-1">Número de Tarjeta</label>
                <input
                  type="text"
                  placeholder="1234 5678 9012 3456"
                  className="w-full p-2 border rounded-md"
                  pattern="\d{16}"
                  required
                  value={datosTarjeta.numero}
                  onChange={(e) => setDatosTarjeta({...datosTarjeta, numero: e.target.value})}
                />
              </div>
              
              <div className="flex gap-3">
                <div className="flex-1">
                  <label className="block mb-1">Vencimiento</label>
                  <input
                    type="text"
                    placeholder="MM/AA"
                    className="w-full p-2 border rounded-md"
                    pattern="\d{2}/\d{2}"
                    required
                    value={datosTarjeta.vencimiento}
                    onChange={(e) => setDatosTarjeta({...datosTarjeta, vencimiento: e.target.value})}
                  />
                </div>
                
                <div className="flex-1">
                  <label className="block mb-1">CVV</label>
                  <input
                    type="text"
                    placeholder="123"
                    className="w-full p-2 border rounded-md"
                    pattern="\d{3}"
                    required
                    value={datosTarjeta.cvv}
                    onChange={(e) => setDatosTarjeta({...datosTarjeta, cvv: e.target.value})}
                  />
                </div>
              </div>
            </div>
          )}

          {metodoPago === 'transferencia' && (
            <div className="mb-4">
              <p className="text-sm bg-black-50 p-3 rounded-md">
                Realice la transferencia a la cuenta: 
                <strong> 0102-0455-55-5555555555</strong>
                <br/>
                Banco: Banco de Venezuela
                <br/>
                RIF: J-123456789
              </p>
            </div>
          )}

          {metodoPago === 'efectivo' && (
            <div className="mb-4">
              <p className="text-sm bg-ligth-50 p-3 rounded-md">
                Debe realizar el pago en nuestras oficinas dentro de las próximas 48 horas
                para completar su inscripción.
              </p>
            </div>
          )}

          {error && <div className="text-red-500 mb-4">{error}</div>}

          <div className="flex justify-end gap-3 mt-6">
            <button
              type="button"
              onClick={onCerrar}
              className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              Confirmar Pago
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ModalInscripcion;