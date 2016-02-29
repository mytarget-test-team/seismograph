Forms
=====

You can to use declarative approach for description UI forms.


Simple UI form
--------------


.. code-block:: python

    from seismograph.ext import selenium
    from seismograph.ext.selenium import forms


    class ExampleForm(forms.UIForm):

        some_field = forms.fields.Input(
            'Some input field',
            value='default value',
            selector=forms.fields.selector(id='some_id'),
        )

        submit = selenium.PageElement(
            selenium.query(
                selenium.query.BUTTON,
                name='some_button',
            ),
            call=lambda we: we.click(),
        )


It's working so


>>> form = ExampleForm(browser)
>>> form.fill()
>>> form.submit()


Update default values for fields
--------------------------------

If you use keyword argument "value" when create instance of any field that you set default value for field in reality.
Any value can be changed. Also, value can be callable object.

Let look how to work with values of fields...


.. code-block:: python

    form = ExampleForm(browser)
    form.update(
        some_field='some text',
    )

    form.fill()
    form.submit()



Also, value can be set for instance of field


.. code-block:: python

    form.some_field.value = 'some text'
    form.fill()
    form.submit()


if you want to save default values for fields after changed that you can use **preserve_original** function as context manager


.. code-block:: python

    with forms.preserve_original(form):
        form.update(
            some_field='some text',
        )

        form.fill()
        form.submit()


Field can be filling by self method. Value is not required param.


.. code-block:: python

    form.some_field.fill('some value')


Default value doesn't got change


Mount form to page as page element
----------------------------------

You can to use form as page element.


.. code-block:: python


    class ExamplePage(selenium.Page):

        example_form = selenium.PageElement(ExampleForm)


It's working so


>>> page = ExamplePage(browser)
>>> page.example_form.fill()
>>> page.example_form.submit()


Required flag
-------------

You can to get marker for field about as required for fill.


.. code-block:: python

    class ExampleForm(forms.UIForm):

        some_field = forms.fields.Input(
            'Some input field',
            required=True,
            value='default value',
            selector=forms.fields.selector(id='some_id'),
        )


Values for validation field
---------------------------

When you want to validate form that you can to use different values for that.


.. code-block:: python

    class ExampleForm(forms.UIForm):

        some_field = forms.fields.Input(
            'Some input field',
            value='default value',
            invalid_value='some invalid value',
            selector=forms.fields.selector(id='some_id'),
        )


Iterators
---------

You can to iterate by fields.


.. code-block:: python

    # iterated by all fields
    for field in forms.iter_fields(form):
        # do something

    # iterated by fields when set invalid_value
    for field in forms.iter_invalid(form):
        # do something

    # iter by fields when required flag is True
    for field in forms.iter_required(form):
        # do something


Also, you can to use "exclude" keyword argument for iterator.


.. code-block:: python

    for field in form.iter_fields(form, exclude=[form.some_field]):
        # do something


How to do remember for fill field
---------------------------------

Form does remember fill field and you can to find usage for that.


.. code-block:: python

    form = ExampleForm(browser)
    form.some_field.fill('some value')

    form.fill()
    # some_field doesn't fill again


Sorted fields for fill
----------------------

Very often we get need to fill fields in the correct order.
You can use "weight" keyword argument for that.

.. code-block:: python

    class ExampleForm(forms.UIForm):

        some_field = forms.fields.Input(
            'Some input field',
            weight=1,
            value='default value',
            selector=forms.fields.selector(id='some_id'),
        )

        another_some_field = forms.fields.TextArea(
            'Some text area',
            weight=2,
            value='Some text',
            selector=forms.fields.selector(id='some_id'),
        )


Fields group
------------

Group like form that collect fields.


.. code-block:: python

    class ExampleGroup(forms.FieldsGroup):

        some_field = forms.fields.Input(
            'Some input field',
            value='default value',
            selector=forms.fields.selector(id='some_id'),
        )


    class ExampleForm(forms.UIForm):

        some_field = forms.fields.Input(
            'Some input field',
            value='default value',
            selector=forms.fields.selector(id='some_id'),
        )

        example_group = forms.make_field(
            ExampleGroup,
        )

        submit = selenium.PageObject(
            selenium.query('button', name='some_button'),
            action=lambda button: button.click(),
        )
