"""
My first application
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from services import database_connection as dbc
import xml.etree.ElementTree as ET

import httpx



class Dentalcare(toga.App):


    def startup(self):
        self.graph_id = 1329732  # change to your own graph id
        self.simulationwindow = 0

        login_box = toga.Box(style=Pack(direction=COLUMN))
        login = toga.Button(
            'Login',
            on_press=self.show_login_window,
            style=Pack(padding=5)
        )
        login_box.add(login)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = login_box
        self.main_window.show()

    def show_login_window(self, widget):

        self.second_window = toga.Window(title='Login')
        self.windows.add(self.second_window)
        login_box = toga.Box(style=Pack(direction=COLUMN))

        username_box = toga.Box(style=Pack(direction=ROW, padding=5))
        user_label = toga.Label(
            'Username: ',
            style=Pack(padding=(0, 10))
        )
        self.user_input = toga.TextInput(style=Pack(flex=1), placeholder='enter your DCR email', value='idasuhr@hotmail.com') # hint use "value = your email" to not have to retype it all the time
        username_box.add(user_label)
        username_box.add(self.user_input)

        password_box = toga.Box(style=Pack(direction=ROW, padding=5))
        passwd_label = toga.Label(
            'Password: ',
            style=Pack(padding=(0, 10))
        )
        self.password_input = toga.PasswordInput(style=Pack(flex=1))
        password_box.add(passwd_label)
        password_box.add(self.password_input)

        login_button = toga.Button(
            'Login',
            on_press=self.login,
            style=Pack(padding=5)
        )

        login_box.add(username_box)
        login_box.add(password_box)
        login_box.add(login_button)

        self.second_window.content = login_box
        self.second_window.show()

    async def login(self, widget):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims",
                                        auth=(self.user_input.value, self.password_input.value))
            print(response.text)
            root = ET.fromstring(response.text)
        except:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}",
                                        auth=(self.user_input.value, self.password_input.value))
            print("no instances")
            print(response.text)
            root = ET.fromstring(response.text)

        self.sims = {}
        self.username = self.user_input.value
        self.password = self.password_input.value
        dbc.db_connect()
        dbc.db_connect()
        role = dbc.execute_query("get_dcr_role", {'email': self.username})
        print(f'[i] Role: {role.fetchone()[0]}')



        #for s in root.findall("trace"):
        #    print(f"[i] id: {s.attrib['id']}, title: {s.attrib['title']}")
        #    self.sims[s.attrib['id']] = "Instance:"+s.attrib['id']
        load_instances = dbc.load_instances()
        for instance in load_instances:
            print(f"[i] id: {instance[1]}, title: MySQL")
            self.sims[instance[1]] = "Instance:"+instance[1]
        self.second_window.close()
        self.show_sim_list()

    def show_sim_list(self):
        container = toga.ScrollContainer(horizontal=False,)
        sims_box = toga.Box(style=Pack(direction=COLUMN))
        container.content = sims_box

        f_button = toga.Button(
            "Delete all instances",
            on_press=self.delete_all_instances,
            style=Pack(padding=5)
        )


        for id, name in self.sims.items():
            g_button = toga.Button(
                name,
                on_press=self.show_enabled_activities,
                style=Pack(padding=5),
                id = id,
            )

            sims_box.add(g_button)
        g_button = toga.Button(
                "Create new instance",
                on_press=self.create_show_enabled_activities,
                style=Pack(padding=5)
        )

        sims_box.add(g_button)
        sims_box.add(f_button)

        self.main_window.content = container


    async def show_enabled_activities(self, widget):
        self.sim_id = widget.id
        enabled_events = await self.get_enabled_events()
        print(enabled_events.json())
        root = ET.fromstring(enabled_events.json())
        events = root.findall('event')
        self.show_activities_window(events)


    async def create_show_enabled_activities(self, widget):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims",
                                         auth=(self.username, self.password))
            self.sim_id = response.headers['simulationid']

            query = (self.graph_id, self.sim_id)
            dbc.execute_instance(query)

            enabled_events = await self.get_enabled_events()
        print(enabled_events.json())
        root = ET.fromstring(enabled_events.json())
        events = root.findall('event')
        self.show_activities_window(events)

    def show_activities_window(self, events):
        if self.simulationwindow != 0:
              self.activities_window.close()
        self.activities_window = toga.Window(title=f'Simulation #{self.sim_id}')
        self.simulationwindow=1
        self.windows.add(self.activities_window)

        self.update_activities_box(events)
        self.activities_window.show()

    async def execute_activity(self, widget):
    # TODO: INSERT CODE HERE TO EXECUTE EVENT widget.id in simulation self.sim_id for graph self.graph.id
    #       RETURN result in response
        async with httpx.AsyncClient() as client:
            self.event_id = widget.id
            response = await client.post(f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims"
                                         f"/{self.sim_id}/events/{self.event_id}",
                                  auth=(self.username, self.password))

        if len(response.text) == 0:
            enabled_events = await self.get_enabled_events()
        else:
            print(f'[!] {response.text}')
        if enabled_events:
            root = ET.fromstring(enabled_events.json())
            events = root.findall('event')
            self.update_activities_box(events)
        else:
            print("[!] No enabled events!")

    async def get_enabled_events(self):
        url = f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims/{self.sim_id}/events?filter=only-enabled"
        async with httpx.AsyncClient() as client:
            return await client.get(url, auth=(self.username, self.password))


    def update_activities_box(self, events):
        activities_box = toga.Box(style=Pack(direction=COLUMN))

        if len(events) >= 1:
            for e in events:
                e_button = toga.Button(
                    text=e.attrib['label'],
                    on_press=self.execute_activity,
                    style=Pack(padding=5),
                    id=e.attrib['id'],
                )
                activities_box.add(e_button)
            self.sims[self.sim_id] = "Instance:" + self.sim_id
            self.show_sim_list()
        else:
            self.activities_window.hide()
            dbc.delete_instance(self.sim_id)
            print("[!] No events to execute!")
            print(self.sims.items())
            self.sims.pop(self.sim_id)
            print(self.sims.items())
            self.show_sim_list()
        self.activities_window.content = activities_box

    async def delete_all_instances(self, widget):
        for sim, hwl in self.sims.items():
            url = f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims/{sim}"
            async with httpx.AsyncClient() as client:
                response = await client.delete(url, auth=(self.username, self.password))
            dbc.delete_instance(sim)
        for key, value in list(self.sims.items()):
            self.sims.pop(key)

        print(self.sims.items())
        self.show_sim_list()



def main():
    return Dentalcare()