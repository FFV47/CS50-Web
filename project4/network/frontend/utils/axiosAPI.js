import axios from "axios";

axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

class axiosAPI {
  constructor(baseURL) {
    this.controller = new AbortController();
    this.instance = axios.create({
      baseURL: baseURL ? baseURL : "",
      signal: this.controller.signal,
    });
    this.response = null;
    this.data = null;
    this.error = null;
  }

  get = async (url) => {
    try {
      this.response = await this.instance.get(url);
      if (this.response) {
        this.data = this.response.data;
      }
    } catch (error) {
      this.error = axiosAPI.apiError(error);
    }

    return { data: this.data, error: this.error };
  };

  post = async (url, data, headers) => {
    try {
      this.response = await this.instance.post(url, data, headers);
      if (this.response) {
        this.data = this.response.data;
      }
    } catch (error) {
      this.error = axiosAPI.apiError(error);
    }

    return { data: this.data, error: this.error };
  };

  put = async (url, data, headers) => {
    try {
      this.response = await this.instance.put(url, data, headers);
      if (this.response) {
        this.data = this.response.data;
      }
    } catch (error) {
      this.error = axiosAPI.apiError(error);
    }

    return { data: this.data, error: this.error };
  };

  delete = async (url) => {
    try {
      this.response = await this.instance.delete(url);
      if (this.response) {
        this.data = this.response.data;
      }
    } catch (error) {
      this.error = axiosAPI.apiError(error);
    }

    return { data: this.data, error: this.error };
  };

  patch = async (url, data, headers) => {
    try {
      this.response = await this.instance.patch(url, data, headers);
      if (this.response) {
        this.data = this.response.data;
      }
    } catch (error) {
      this.error = axiosAPI.apiError(error);
    }

    return { data: this.data, error: this.error };
  };

  abort = () => {
    this.instance.abort();
  };

  static apiError = (error) => {
    let message;
    let data = null;
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      message = `Server responded. Error: ${error.message}`;
      data = error.response.data;
    } else if (error.request) {
      // The request was made but no response was received
      // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
      // http.ClientRequest in node.js
      message = `No response received from the server. Error: ${error.message}`;
    } else {
      // Something happened in setting up the request that triggered an Error
      message = `Request error: ${error.message}`;
    }

    return { data, message };
  };
}

export default axiosAPI;
