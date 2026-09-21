##this script is used to create a happy face on a TXT file. It prouposes is to test the job creation on github workflows.

def main():
    with open("happy_face.txt", "w") as f:
        f.write("     *****     \n")
        f.write("   *       *   \n")
        f.write("  *  O   O  *  \n")
        f.write(" *     ^     * \n")
        f.write(" *    '-'    * \n")
        f.write("  *         *  \n")
        f.write("   *       *   \n")
        f.write("     *****     \n")

if __name__ == "__main__":
    main()