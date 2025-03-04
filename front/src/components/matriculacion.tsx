import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ModalInscripcion from './modalinscripcion';
import { FaShoppingCart } from 'react-icons/fa';

interface Courses {
  curso_id: number;
  nombre: string;
  cedula_instructor: string;
  costo: number;
  duracion: number;
  estado: boolean;
  limite_estudiante: number;
  modalidad_id: string;
}

export const ListaCourses: React.FC = () => {
  const [courses, setCourses] = useState<Courses[]>([]);
  const [error, setError] = useState('');
  const [modalAbierto, setModalAbierto] = useState(false);
  const [cedulaUsuario, setCedulaUsuario] = useState<number | null>(null);
  const [carrito, setCarrito] = useState<Courses[]>([]);
  const [carritoVisible, setCarritoVisible] = useState(false);

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const response = await axios.get('http://localhost:5000/lista_cursos');
        setCourses(response.data);
      } catch (error: any) {
        setError(error.response?.data?.error || 'Error al obtener Cursos');
      }
    };

    fetchCourses();

    const fetchCedula = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const response = await axios.get('http://localhost:5000/ruta_protegida', {
            headers: { Authorization: `Bearer ${token}` },
          });
          setCedulaUsuario(response.data.cedula);
        } catch (error) {
          console.error('Error al obtener la cédula:', error);
        }
      }
    };

    fetchCedula();

    const carritoGuardado = localStorage.getItem('carrito');
    if (carritoGuardado) {
      setCarrito(JSON.parse(carritoGuardado));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('carrito', JSON.stringify(carrito));
  }, [carrito]);

  const agregarAlCarrito = (curso: Courses) => {
    setCarrito((prevCarrito) => {
      const cursoExistente = prevCarrito.find((c) => c.curso_id === curso.curso_id);
      if (!cursoExistente) {
        return [...prevCarrito, curso];
      }
      return prevCarrito;
    });
  };

  const eliminarDelCarrito = (cursoId: number) => {
    setCarrito((prevCarrito) => prevCarrito.filter((curso) => curso.curso_id !== cursoId));
  };

  const handleCerrarModal = () => {
    setModalAbierto(false);
    setError('');
  };

  const handlePago = async (pago: string) => {
    if (carrito.length === 0 || cedulaUsuario === null) return;

    const token = localStorage.getItem('access_token');
    if (!token) {
      setError('Debe iniciar sesión para realizar el pago');
      return;
    }

    try {
      await axios.post(
        'http://localhost:5000/pago',
        {
          cursos: carrito.map(curso => curso.curso_id),
          pago: pago,
          total: carrito.reduce((sum, curso) => sum + curso.costo, 0)
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      // Limpiar carrito después de pago exitoso
      setCarrito([]);
      setModalAbierto(false);
      setError('');
    } catch (error: any) {
      setError(error.response?.data?.error || 'Error al procesar el pago');
    }
  };

  const toggleCarrito = () => {
    setCarritoVisible(!carritoVisible);
  };

  return (
    <div className="flex flex-wrap gap-5 p-5 relative">
      <div className="absolute top-5 right-5">
        <FaShoppingCart className="text-2xl cursor-pointer" onClick={toggleCarrito} />
        {carrito.length > 0 && (
          <span className="absolute top-0 right-0 bg-red-500 text-black rounded-full px-1 text-xs">
            {carrito.length}
          </span>
        )}
      </div>

      {courses.map((course) => (
        <div key={course.curso_id} className="border border-black-300 rounded-lg p-5 w-72 shadow-md">
          <h3 className="mt-0 text-lg font-semibold">{course.nombre}</h3>
          <p>Instructor: {course.cedula_instructor}</p>
          <p>Costo: {course.costo} Bolívares</p>
          <p>Duración: {course.duracion}</p>
          <p>Estado: {course.estado ? 'Activo' : 'Inactivo'}</p>
          <p>Límite de Estudiantes: {course.limite_estudiante}</p>
          <p>Modalidad: {course.modalidad_id}</p>
          <button 
            onClick={() => agregarAlCarrito(course)} 
            className="mt-3 inline-block bg-green-600 text-white py-2 px-4 rounded hover:bg-green-500 transition"
          >
            Agregar al carrito
          </button>
        </div>
      ))}

      {carritoVisible && (
        <div className="absolute top-16 right-5 bg-black border border-gray-300 rounded-lg shadow-lg p-5 w-80">
          <h2 className="text-xl font-bold mb-4">Carrito de Compras</h2>
          {carrito.length === 0 ? (
            <p>No hay cursos en el carrito.</p>
          ) : (
            <div>
              {carrito.map((curso) => (
                <div key={curso.curso_id} className="border-b border-gray-200 py-2">
                  <h3 className="font-semibold">{curso.nombre}</h3>
                  <p>Costo: {curso.costo} Bolívares</p>
                  <button 
                    onClick={() => eliminarDelCarrito(curso.curso_id)} 
                    className="mt-1 inline-block bg-red-600 text-white py-1 px-2 rounded hover:bg-red-500 transition"
                  >
                    Eliminar
                  </button>
                </div>
              ))}
              <div className="mt-4 font-bold text-lg">
                Total: {carrito.reduce((sum, curso) => sum + curso.costo, 0)} Bs
              </div>
              <button 
                onClick={() => setModalAbierto(true)} 
                className="mt-3 w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-500 transition"
              >
                Proceder al Pago
              </button>
            </div>
          )}
        </div>
      )}

      {modalAbierto && (
        <ModalInscripcion
          carrito={carrito}
          cedulaUsuario={cedulaUsuario!}
          onPago={handlePago}
          onCerrar={handleCerrarModal}
          error={error}
        />
      )}
    </div>
  );
};

export default ListaCourses;