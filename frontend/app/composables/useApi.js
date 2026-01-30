
export const useApi = () => {
    const baseURL = 'http://localhost:8000/api'

    return {

        // Resources
        fetchResources: () => $fetch(`${baseURL}/resources/get_resources`),
        createResource: (data) => $fetch(`${baseURL}/resources/create_resource`, {
            method: 'POST',
            body: data
        }),
        updateResource: (id, data) => $fetch(`${baseURL}/resources/update_resource/${id}`, {
            method: 'POST',
            body: data
        }),
        fetchResourceTypes: () => $fetch(`${baseURL}/resourceTypes/get_resourceTypes`),


        // DisruptionTypes
        fetchDisruptionTypes: () => $fetch(`${baseURL}/disruptionTypes/get_disruptionTypes`),


        // Disruptions
        fetchDisruptions: () => $fetch(`${baseURL}/disruptions/get_disruptions`),
        updateDisruption: (id, data) => $fetch(`${baseURL}/disruptions/update_disruption/${id}`, {
            method: 'POST',
            body: data
        }),
        createDisruption: (data) => $fetch(`${baseURL}/disruptions/create_disruption`, {
            method: 'POST',
            body: data
        }),

        // Hilfsfunktion zum Speichern (POST für neu, PUT für edit)
        saveResource: (payload, id = null) => {
            const url = id
                ? `${baseURL}/resources/update_resource/${id}/`
                : `${baseURL}/resources/create_resource/`

            return $fetch(url, {
                method: 'POST',
                body: payload
            })
        },

        // Hilfsfunktion zum Speichern (POST für neu, PUT für edit)
        saveDisruption: (payload, id = null) => {
            const url = id
                ? `${baseURL}/disruptions/update_disruption/${id}/`
                : `${baseURL}/disruptions/create_disruption/`

            return $fetch(url, {
                method: id ? 'PUT' : 'POST',
                body: payload
            })
        }
    }
}