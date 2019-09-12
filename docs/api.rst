API
===

.. automodule:: dbpool

   
   .. autoexception:: PoolError

   .. autoexception:: NoAvailableConnectionError

   .. autoexception:: CreateConnectionError

   .. autoexception:: TestConnectionError

   .. autoclass:: PoolOption

   .. autoclass:: PooledConnection

      .. automethod:: close

   .. autoclass:: ConnectionPool

      .. automethod:: close
      .. automethod:: borrow_connection
