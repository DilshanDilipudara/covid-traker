from h2o_wave import main, app, Q, ui


_id = 0


class Person:
    def __init__(self, name: str, nid: str, status: str ):
        global _id
        _id += 1
        self.id = f'I{_id}'
        self.name = name
        self.nid = nid
        self.status = status


# Create a person

async def new_person(q: Q):
    # Display an input form
    q.page['form'] = ui.form_card(
        box='1 1 3 10',
        items=[
            ui.text_l('Add New Person'),
            ui.textbox(name='name', label='Name : ', multiline=True),
            ui.textbox(name='nid', label='National ID Number : ', multiline=True),
            ui.textbox(name='status', label='Positive/Negative : ', multiline=True),
            ui.buttons([
                ui.button(name='add_todo', label='Add', primary=True),
                ui.button(name='show_todos', label='Back'),
            ]),
        ])
    await q.page.save()

persons = [Person(name="dishan", nid="9415266V", status='Negative'),
           Person(name="sahan", nid="9415266V", status='Positive'),
           Person(name="razer", nid="91252222V", status='Negative'),
           Person(name="mozar", nid="95225541V", status='Positive'),
           Person(name="zuki", nid="92454785V", status='Negative')]


async def add_person(q: Q):
    q.user.persons.insert(Person(q.args.name, q.args.nid, q.args.status))
    global persons
    persons = q.client.persons
    for person in persons:
        if person.id in q.args:
            person.done = q.args[person.id]
    await show_persons(q)

# Build a lookup of person for convenience
persons_lookup = {person.id: person for person in persons}


# Create columns for our issue table.
columns = [
    ui.table_column(name="id", label="ID"),
    ui.table_column(name='name', label='Name'),
    ui.table_column(name='nid', label='National ID Number'),
    ui.table_column(name='status', label='Negative/Positive'),
]


def make_table(allow_multiple_selection=False):
    return ui.table(
        name='persons',
        columns=columns,
        rows=[ui.table_row(name=person.id, cells=[person.id, person.name, person.nid, person.status]) for person in persons],
        multiple=allow_multiple_selection
    )


async def edit_multiple(q: Q):
    q.page['form'] = ui.form_card(
        box='2 2 10 10',
        items=[
            make_table(allow_multiple_selection=True),  # This time, allow multiple selections
            ui.buttons([
                ui.button(name='test_positive', label='Positive Selected', primary=True),
                ui.button(name='test_negative', label='Negative Selected', primary=True),

            ]),
        ]
    )
    await q.page.save()


async def show_persons(q: Q):
    q.page['form'] = ui.form_card(
        box='1 1 6 10',
        items=[
            ui.text_l('Covid-19 Tracker'),
            ui.buttons([ui.button(name='new_person', label='Add Patient Details...', primary=True)]),
            make_table(),
            ui.buttons([ui.button(name='edit_multiple', label='Edit Patient...', primary=True)]),
        ]
    )

    await q.page.save()


async def show_person(q: Q, person_id: str):
    person = persons_lookup[person_id]
    person.views += 1

    q.client.active_person_id = person_id

    q.page['form'] = ui.form_card(
        box='1 1 4 10',
        items=[
            ui.text_xl(f'Person {person.id}'),
            ui.text(person.id),
            ui.text(person.name),
            ui.text(person.nid),
            ui.buttons([
                ui.button(
                    name='close_person' if person.status == 'Negative' else 'test_positive',
                    label="Close Person" if person.status == 'Negative' else "Test Positive",
                    primary=True,
                ),
                ui.button(name='back', label='Back'),
            ]),
        ]
    )

    await q.page.save()


@app('/covid')
async def serve(q: Q):
    if q.args.edit_multiple:
        await edit_multiple(q)
    elif q.args.new_person:
        await new_person(q)
    elif q.args.add_person:  # Add a person.
        add_person(q)
    elif q.args.persons:
        await show_person(q, q.args.issues[0])
    else:
        await show_persons(q)