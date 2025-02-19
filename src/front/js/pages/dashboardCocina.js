import React, { useEffect } from "react";
import { Link } from "react-router-dom";
import { Context } from "../store/appContext"; 

const DashboardCocina = () => {
  
  const { store, actions } = React.useContext(Context);
  const { orders } = store;  // Access orders from the store

  useEffect(() => {
    
    actions.getOrders();
  }, [actions]);

  if (!orders.length) return <p>Loading orders...</p>;

  return (
    <div className="container mt-5">
      <h1 className="mb-2">Listado De Menus</h1>
      <div className="d-flex justify-content-between mt-4 p-5">
        <div className="d-flex">
          <button
            className="btn btn-secondary dropdown-toggle me-2"
            type="button"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            Action
          </button>
          <ul className="dropdown-menu">
            <li>
              <a className="dropdown-item" href="#">
                Action
              </a>
            </li>
            <li>
              <a className="dropdown-item" href="#">
                Another action
              </a>
            </li>
            <li>
              <a className="dropdown-item" href="#">
                Something else here
              </a>
            </li>
          </ul>
          <form className="d-flex justify-content-start" role="search">
            <input
              className="form-control me-2"
              type="search"
              placeholder="Search"
              aria-label="Search"
            />
            <button className="btn btn-primary" type="submit">
              Buscar
            </button>
          </form>
        </div>
        <div>
          <Link to="/add/menu">
            <button className="btn btn-primary" role="button">
              Añadir Menu
            </button>
          </Link>
        </div>
      </div>
      <div>
        <table className="table table-secondary table-striped mt-3">
          <thead>
            <tr>
              <th scope="col">
                <div className="form-check">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    id="flexCheckIndeterminate"
                  />
                  <label
                    className="form-check-label"
                    htmlFor="flexCheckIndeterminate"
                  ></label>
                </div>
              </th>
              <th scope="col">Fecha</th>
              <th scope="col">Tipo</th>
              <th scope="col">Descripcion</th>
              <th scope="col">Estado</th>
              <th scope="col">Categoria</th>
              <th scope="col">Stock</th>
              <th scope="col">Imagen</th>
              <th scope="col">Precio</th>
              <th scope="col"></th>
            </tr>
          </thead>
          <tbody>
            {orders.length === 0 ? (
              <tr>
                <td colSpan="10">No orders found.</td>
              </tr>
            ) : (
              orders.map((order, index) => (
                <tr key={order.id || index}>
                  <th scope="row">
                    <div className="form-check">
                      <input
                        className="form-check-input"
                        type="checkbox"
                        id={`orderCheck${index}`}
                      />
                      <label
                        className="form-check-label"
                        htmlFor={`orderCheck${index}`}
                      ></label>
                    </div>
                  </th>
                  <td>{new Date(order.date).toLocaleDateString() || "N/A"}</td>
                  <td>{order.product.type || "N/A"}</td>
                  <td>{order.product.description || "N/A"}</td>
                  <td>{order.status || "N/A"}</td>
                  <td>{order.product.name || "N/A"}</td>
                  <td>{order.product.stock || 0}</td>
                  <td>
                    <img
                      src={order.product.image || "placeholder.jpg"}
                      alt={order.product.name || "Product"}
                      style={{ width: "50px" }}
                    />
                  </td>
                  <td>{`$${order.product.price || 0}`}</td>
                  <td className="d-flex justify-content-end">
                    <Link to="/add/menu" className="btn">
                      <i className="fa-solid fa-pen"></i>
                    </Link>
                    <button
                      className="btn dropdown-toggle me-2"
                      type="button"
                      data-bs-toggle="dropdown"
                      aria-expanded="false"
                    >
                      <i className="fa-solid fa-ellipsis"></i>
                    </button>
                    <ul className="dropdown-menu">
                      <li>
                        <a className="dropdown-item" href="#">
                          Edit
                        </a>
                      </li>
                      <li>
                        <a className="dropdown-item" href="#">
                          Delete
                        </a>
                      </li>
                    </ul>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DashboardCocina;
