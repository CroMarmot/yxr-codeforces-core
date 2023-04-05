User 
======

Quick Start
-----------

.. code-block:: python

    import asyncio
    from codeforces_core.httphelper import HttpHelper
    from codeforces_core.account import async_login
    from codeforces_core.contest_meta import async_contest_meta

    async def demo():
      http = HttpHelper()
      await http.open_session()
      await async_login(http=http, handle='<handle>', password='<password>')
      result = await async_contest_meta(http=http, contest_id = '1779')
      print(result)
      await http.close_session()
    
    asyncio.run(demo())

.. toctree::
    :maxdepth: 3

    00_install
    01_examples
    02_about